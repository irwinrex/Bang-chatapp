import re
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from account.models import CustomUser  # Assuming your user model is CustomUser
from .validators import validate_username, validate_password, validate_unique_email, validate_phone_number, validate_user_for_deletion

class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[validate_username])
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(
        validators=[
            EmailValidator(message="Enter a valid email address."),
            validate_unique_email  # Ensure the email is unique
        ]
    )
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Enter a valid phone number. It must be 9 to 15 digits long, and may include a country code starting with +."
            ),
            validate_phone_number  # Ensure the phone number is unique
        ]
    )
    age = serializers.IntegerField(min_value=10, max_value=99)
    sex = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])

    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            age=validated_data['age'],
            sex=validated_data['sex']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserDeleteSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Validate if the user exists and if the credentials match
        try:
            validate_user_for_deletion(username, email, password)
        except ValidationError as e:
            raise serializers.ValidationError({"detail": str(e)})

        return data

    def delete_user(self):
        username = self.validated_data['username']
        email = self.validated_data['email']
        user = CustomUser.objects.get(username=username, email=email)
        user.delete()
        return {"detail": "User deleted successfully"}
