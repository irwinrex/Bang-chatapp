import re
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate
from account.models import CustomUser  # Assuming your user model is CustomUser

def validate_username(value):
    if not re.match(r'^[a-z0-9]+$', value):
        raise serializers.ValidationError("Username must contain only lowercase letters and numbers.")
    if CustomUser.objects.filter(username=value).exists():
        raise serializers.ValidationError("This username is already taken.")
    return value

def validate_password(value):
    if len(value) < 18:
        raise serializers.ValidationError("Password must be at least 18 characters long.")
    if not re.search(r'[a-z]', value):
        raise serializers.ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'[A-Z]', value):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'\d', value):
        raise serializers.ValidationError("Password must contain at least one digit.")
    if not re.search(r'[!@#\$%\^&\*]', value):
        raise serializers.ValidationError("Password must contain at least one special character.")
    return value

def validate_unique_email(value):
    if CustomUser.objects.filter(email=value).exists():
        raise serializers.ValidationError("This email address is already in use.")
    return value

def validate_phone_number(value):
    if CustomUser.objects.filter(phone_number=value).exists():
        raise serializers.ValidationError("This phone number is already in use.")
    return value

def validate_user_for_deletion(username, email, password):
    try:
        # Check if the user exists with the given username and email
        user = CustomUser.objects.get(username=username, email=email)
    except CustomUser.DoesNotExist:
        raise ValidationError("User with the provided username and email does not exist.")

    # Use the authenticate method to check if the password is correct
    authenticated_user = authenticate(username=user.email, password=password)
    
    if authenticated_user is None:
        raise ValidationError("Password is incorrect.")
    
    return user