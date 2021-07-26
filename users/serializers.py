from rest_framework import serializers
from users.models import User, RefreshToken


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar']


class UserInitializeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}



class UserLogInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class RefreshTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefreshToken
        fields = ['user', 'token']


class UserChangePasswordSerializer(serializers.Serializer):
    model = User
    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class UserForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
