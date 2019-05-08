"""
Serializer for Conntact app user accounts
"""
from rest_framework import serializers
from user.models import (User, BlackListedToken)

class UserSerializer(serializers.ModelSerializer):
    """
    Serialzer class for Application user
    """
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2','email', 'phone', 'deleted_at')

    def validate(self, data):
        """
        Validation method for checking password validation
        """
        original_password = data.get('password')
        confirm_password = data.pop('password2')
        
        if original_password != confirm_password:
            raise serializers.ValidationError('Entered password did not matched')
        return data
    
    def create(self, validated_data):
        """
        Overriding create method to save user mobile and password
        """
        user = User.objects.filter(phone=validated_data.get('phone'))
        if user.count() > 0:
            raise serializers.ValidationError('Entered mobile number is already registered')
        user_obj = User.objects.create(username=validated_data.get('username'),
                                        email=validated_data.get('email'), phone=validated_data.get('email'))  
        user_obj.set_password(validated_data.get('password'))
        user_obj.save()
        return user_obj

    def update(self, instance, validated_data):
        """
        Overriding update method to update user record
        """
        if instance.phone != validated_data.get('phone'):
            user = User.objects.filter(phone=validated_data.get('phone'))
            if user.count() > 0:
                raise serializers.ValidationError('Entered mobile number is already registered')

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance

class BlackListedTokenSerializer(serializers.ModelSerializer):
    """
    Serializer class for blacklisted token
    """
    class Meta:
        model = BlackListedToken
        fields = ('token', 'user')