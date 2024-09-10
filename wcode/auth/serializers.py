from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import re

def custom_validate_email(value):
    # Check if email ends with '.com' and contains '@'
    if not value.endswith('.com') or '@' not in value:
        raise serializers.ValidationError("Enter a valid email address")
    return value

def validate_username(value):
    # Check if username contains only lowercase letters and numbers
    if not re.match(r'^[a-z0-9]+$', value):
        raise serializers.ValidationError("Username must contain only lowercase letters and numbers.")
    return value

def validate_password(value):
    # Ensure password length is between 8 and 18 characters
    if len(value) < 8 or len(value) > 18:
        raise serializers.ValidationError("Password must be between 8 and 18 characters long.")
    return value

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="This email is already in use."),
            custom_validate_email
        ]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="This username is already in use."),
            validate_username
        ]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']  # Django handles the hashing
        )
        return user
