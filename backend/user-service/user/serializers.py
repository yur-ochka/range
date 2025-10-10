from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with basic user information."""
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_active', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model with user profile information."""
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'date_of_birth']


class UserWithProfileSerializer(serializers.ModelSerializer):
    """Serializer for User model that includes related UserProfile info."""
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_active', 'date_joined', 'profile']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password validation."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name',
                  'last_name', 'password', 'password_confirm']

    def validate_email(self, value):  # Unique email check
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def validate_username(self, value):  # Unique username check
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists.")
        return value

    def validate_password(self, value):  # Password validation
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):  # Password check
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        return attrs

    def create(self, validated_data):  # Create user
        validated_data.pop('password_confirm', None)

        user = User.objects.create_user(**validated_data)

        UserProfile.objects.create(user=user)

        return user