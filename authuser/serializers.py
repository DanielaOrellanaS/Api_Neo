from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth.models import User
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class CustomLoginSerializer(LoginSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type':'password'})
    email = serializers.HiddenField(default=None)

    def validate(self, attrs):
        if 'username' in attrs and attrs['username'] == '':
            raise serializers.ValidationError('The field "username" is required.')
        return super().validate(attrs)
    
    