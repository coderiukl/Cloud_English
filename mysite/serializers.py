from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'email', 'name', 'first_name', 'last_name', 'last_login', 'joined_date']

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type':'password'},
        label='Confirm Password'
    )
    class Meta:
        model = User
        fields = ['email', 'password' ,'password2']
        extra_kwargs = {
            'password':{'write_only': True, 'style':{'input_type':'password'}}
        }
    def validate(self,data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            validated_data['email'],
            validated_data['password'],
        )
        return user

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type':'password'})

    class Meta:
        model = User
        fields = ['email', 'password']

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError as e:
            raise serializers.ValidationError({'refresh': 'Token is invalid or already blacklisted'})

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type':'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type':'password'})

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("New password must be at least 8 characters long.")
        return value
    