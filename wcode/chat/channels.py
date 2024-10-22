import os
from pathlib import Path
import environ
from pulsar import Client as PulsarClient
from channels.layers import BaseChannelLayer
from asgiref.sync import sync_to_async
import asyncio
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Pulsar settings
PULSAR_SERVICE_URL = env('PULSAR_SERVICE_URL')
PULSAR_ADMIN_URL = env('PULSAR_ADMIN_URL')

# Set up logging
logger = logging.getLogger(__name__)

class PulsarChannelLayer(BaseChannelLayer):
    def __init__(self):
        self.client = PulsarClient(PULSAR_SERVICE_URL)
        self.producer = self.client.create_producer('django-channel-topic')

    async def send(self, channel, message):
        """Send a message to the specified channel."""
        try:
            # Convert the message to a string format
            await sync_to_async(self.producer.send)(message.encode('utf-8'))
            logger.info(f"Message sent to {channel}: {message}")
        except Exception as e:
            logger.error(f"Failed to send message to {channel}: {e}")

    async def receive(self, channel):
        """Receive messages from the specified Pulsar topic."""
        consumer = self.client.subscribe(channel, subscription_name='django-channel-subscription')
        while True:
            try:
                msg = await asyncio.get_event_loop().run_in_executor(None, consumer.receive)
                consumer.acknowledge(msg)
                logger.info(f"Message received from {channel}: {msg.data().decode('utf-8')}")
                return msg.data().decode('utf-8')  # Return the message as a string
            except Exception as e:
                logger.error(f"Error receiving message from {channel}: {e}")
                await asyncio.sleep(1)  # Optional: Wait before retrying

    async def close(self):
        """Close the Pulsar client connection."""
        await sync_to_async(self.producer.close)()
        await sync_to_async(self.client.close)()
        logger.info("Pulsar client closed successfully.")
