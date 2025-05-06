from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя.
    """
    class Meta:
        model = UserProfile
        fields = ['phone', 'address']


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователя.
    """
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'profile']
    
    def validate(self, data):
        """
        Проверяет, что пароли совпадают.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        return data
    
    def create(self, validated_data):
        """
        Создает пользователя и его профиль.
        """
        validated_data.pop('password_confirm')
        profile_data = validated_data.pop('profile', {})
        
        # Создаем пользователя
        user = User.objects.create_user(**validated_data)
        
        # Обновляем профиль пользователя, если есть данные
        if profile_data:
            for attr, value in profile_data.items():
                setattr(user.profile, attr, value)
            user.profile.save()
        
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Сериализатор для смены пароля.
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """
        Проверяет, что новые пароли совпадают.
        """
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Новые пароли не совпадают."})
        return data 