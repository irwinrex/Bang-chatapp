import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import get_object_or_404
from account.models import CustomUser
from django.contrib.auth import get_user_model
import jwt  # Import for JWT handling

# Set up logging
logger = logging.getLogger(__name__)

def decode_jwt(token):
    """Decode the JWT token and return the user object."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = get_user_model().objects.get(id=payload['user_id'])
        logger.info(f"User authenticated: {user.username}")
        return user
    except (jwt.ExpiredSignatureError, jwt.DecodeError, get_user_model().DoesNotExist) as e:
        logger.error(f"JWT decoding error: {e}")
        return None

@csrf_exempt
def authenticate_and_create_chatroom(request):
    """Authenticate user and create a chatroom by chatIDs."""
    if request.method == 'POST':
        data = json.loads(request.body)
        username1 = data.get('username1')
        username2 = data.get('username2')

        # Extract the Bearer token from the Authorization header
        token = request.headers.get('Authorization', '').split(' ')[-1]

        # Decode the JWT token
        current_user = decode_jwt(token)
        if not current_user:
            logger.warning("Failed authentication: Invalid token provided.")
            return JsonResponse({'error': 'Invalid token'}, status=401)

        try:
            # Fetch users based on provided usernames
            user1 = get_object_or_404(CustomUser, username=username1)
            user2 = get_object_or_404(CustomUser, username=username2)

            # Ensure the current user is one of the users creating the chatroom
            if current_user.id not in {user1.id, user2.id}:
                logger.warning("Unauthorized attempt to create chatroom.")
                return JsonResponse({'error': 'You are not authorized to create this chatroom.'}, status=403)

            # Create a unique room name based on their chatIDs
            room_name = f'chat_{user1.chatID}_{user2.chatID}'

            logger.info(f"Chatroom created: {room_name} between {username1} and {username2}")

            return JsonResponse({
                'message': 'Chatroom created',
                'room_name': room_name,
                'user1_chatID': str(user1.chatID),
                'user2_chatID': str(user2.chatID)
            })

        except Exception as e:
            logger.error(f"Error creating chatroom: {e}")
            return JsonResponse({'error': 'Could not create chatroom'}, status=500)

    logger.warning("Invalid request method; only POST is allowed.")
    return JsonResponse({'error': 'Invalid request method'}, status=405)
