from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserCreateSerializer,UserDeleteSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

# Assuming CustomUser is your user model
User = get_user_model()

class CreateUserView(APIView):
    # Setting permission to AllowAny so that anyone can create a user
    permission_classes = [AllowAny]

    def post(self, request):
        # Creating a new user with the data provided in the request
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new user if the data is valid
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if the data is invalid


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if the user exists in the database
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the provided password matches the user's password
        if not user.check_password(password):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # If credentials are valid, generate a JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
            if user:
                if user.check_password(password):
                    # Delete the user from the database
                    user.delete()
                    return Response({"detail": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
                
            else:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            