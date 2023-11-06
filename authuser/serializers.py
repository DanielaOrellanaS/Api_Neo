from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth.models import User
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model = User
        fields = ['id','email','username','is_active','password']

class CustomLoginSerializer(LoginSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type':'password'})
    email = serializers.HiddenField(default=None)

    def validate(self, attrs):
        if 'username' in attrs and attrs['username'] == '':
            raise serializers.ValidationError('The field "username" is required.')
        return super().validate(attrs)