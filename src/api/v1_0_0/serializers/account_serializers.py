"""
Serializer for Conntact app user accounts
"""
from rest_framework import serializers
from account.models import (AppUser, BlackListedToken)

class AppUserSerializer(serializers.ModelSerializer):
    """
    Serialzer class for Application user
    """
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = AppUser
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
        user = AppUser.objects.filter(phone=validated_data.get('phone'))
        if user.count() > 0:
            raise serializers.ValidationError('Entered mobile number is already registered')
        user_obj = AppUser.objects.create(username=validated_data.get('username'),
                                        email=validated_data.get('email'), phone=validated_data.get('email'))  
        user_obj.set_password(validated_data.get('password'))
        user_obj.save()
        return user_obj

    def update(self, instance, validated_data):
        """
        Overriding update method to update user record
        """
        if instance.phone != validated_data.get('phone'):
            user = AppUser.objects.filter(phone=validated_data.get('phone'))
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
    """
    class Meta:
        model = BlackListedToken
        fields = ('token', 'user')
