import json
import logging
from pulsar import Client as PulsarClient
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from .mongo import save_chat_message  # Import save_chat_message function
import jwt  # Import for JWT handling
from account.models import CustomUser  # Adjust the import based on your user model

# Set up logging
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Extract the Bearer token from headers
        token = self._get_token_from_headers()

        # Decode the JWT token to extract user information
        current_user = self.decode_jwt(token)
        if current_user is None:
            await self.close()  # Close the connection if the user is not authenticated
            return

        self.username = current_user.username
        self.chatID = current_user.chatID  # Assuming you have a chatID attribute in your user model

        # Join room group and accept connection
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        try:
            # Initialize Pulsar client and subscribe to the topic
            self.pulsar_client = PulsarClient(settings.PULSAR_SERVICE_URL)
            self.consumer = self.pulsar_client.subscribe(self.room_name, subscription_name='chatroom')

            # Start a background task to listen for messages
            self.listen_task = self.channel_layer.create_task(self.listen_for_messages())
            logger.info(f"User {self.username} connected to chatroom: {self.room_name}")

        except Exception as e:
            logger.error(f"Failed to connect to Pulsar: {e}")
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Cleanup Pulsar resources
        await self.cleanup_pulsar()

        # Cancel the listening task if it is still running
        if hasattr(self, 'listen_task'):
            self.listen_task.cancel()

        logger.info(f"User {self.username} disconnected from chatroom: {self.room_name}")

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            receiver = text_data_json.get('receiver')  # Get receiver if available

            # Save the message to MongoDB
            save_chat_message(self.room_name, self.username, message)  # Save chat message

            # Send message to Pulsar topic
            await self.send_message_to_pulsar(message)

            # Send the message to the group
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message',
                'message': message,
                'sender': self.username,  # Include sender info
                'receiver': receiver  # Include receiver info
            })
            logger.info(f"Message sent to Pulsar: {message}")

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            logger.error(f"Error receiving message: {e}")

    async def chat_message(self, event):
        """Send messages to WebSocket clients."""
        message = event['message']
        sender = event['sender']
        receiver = event.get('receiver', 'Unknown')  # Get receiver if available

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver  # Include receiver info in the response
        }))

    async def listen_for_messages(self):
        """Listen for messages from the Pulsar topic."""
        while True:
            try:
                msg = await self.channel_layer.run_in_executor(None, self.consumer.receive)
                message = msg.data().decode('utf-8')
                self.consumer.acknowledge(msg)

                # Send the received message to the WebSocket
                await self.send(text_data=json.dumps({'message': message}))
                logger.info(f"Message received from Pulsar: {message}")

            except Exception as e:
                logger.error(f"Error listening for messages: {e}")
                break  # Exit loop on error to avoid infinite errors

    async def cleanup_pulsar(self):
        """Cleanup Pulsar resources."""
        try:
            if hasattr(self, 'consumer'):
                self.consumer.close()
            if hasattr(self, 'pulsar_client'):
                self.pulsar_client.close()
        except Exception as e:
            logger.error(f"Error during Pulsar cleanup: {e}")

    async def send_message_to_pulsar(self, message):
        """Send a message to the Pulsar topic."""
        try:
            producer = self.pulsar_client.create_producer(self.room_name)
            producer.send(message.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending message to Pulsar: {e}")

    def decode_jwt(self, token):
        """Decode the JWT token and return the user object."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return CustomUser.objects.get(id=payload['user_id'])
        except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist) as e:
            logger.error(f"JWT decoding error: {e}")
            return None

    def _get_token_from_headers(self):
        """Extract the Bearer token from the headers."""
        token = dict(self.scope['headers']).get(b'authorization', b'').decode('utf-8').split(' ')[-1]
        return token
