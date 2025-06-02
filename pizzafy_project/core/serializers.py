from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User as CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'role']

    def create(self, validated_data):
        
        password = validated_data.get('password')
        role = validated_data.get('role', 'Customer')
        user = get_user_model().objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            role=role
        )
        
        user.set_password(password)
        user.save()
        return user