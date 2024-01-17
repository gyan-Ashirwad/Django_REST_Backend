from .models import CustomUser as User, UserProfile
from enum import unique
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password


class RegisterSerializer(serializers.Serializer):
    # email = serializers.EmailField(required=True, validators=[
    #     UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(required=True, max_length=50)
    last_name = serializers.CharField(required=True, max_length=50)
    mobile_no = serializers.CharField(required=True, min_length=7, max_length=15, validators=[
        UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True, max_length=50)
    # username = serializers.CharField(required=True, max_length=50)
    

    # class Meta:
    #     # model = User
    #     fields = ['first_name', 'last_name', 'username', 'email',
    #               'password', 'password2', 'mobile_no']

        # extra_kwargs = {
        #     'password': {'write_only': True},
        # }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs
    
    # def validate_username(self, attrs):
    #     if attrs:
    #         existing_user = User.objects.get(username=attrs).first()
    #         print("==========================",existing_user)
    #         if existing_user:
    #             raise serializers.ValidationError(
    #                 {"username": "Username already exists."})
    #     return attrs


class UserLoginSerializer(serializers.Serializer):
    # email = serializers.EmailField(required=True, error_messages={
    #     'required': 'Please enter a valid email address.',
    #     'invalid': 'Please enter a valid email address.',
    #     'blank': 'Email address may not be blank'
    # })
    
    username = serializers.CharField(max_length=30, required=True, error_messages={
        'required': 'Please enter a valid username.',
        'invalid': 'Please enter a valid username.',
        'blank': 'username may not be blank'})
    
    password = serializers.CharField(
        max_length=128, write_only=True, required=True)
    token = serializers.CharField(max_length=255, read_only=True)
    

class UserSerializer(serializers.ModelSerializer):
    
    profile = serializers.SerializerMethodField('get_profile')
    
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','mobile_no','profile']
        
    def get_profile(self, obj):
        profile = UserProfile.objects.filter(user=obj.id).first()
        print("🚀 ~ file: serializers.py:74 ~ profile:", profile)
        if profile:
            return profile.profile.url
        
        
        
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # username = serializers.CharField(source='user.username')
    # profile = serializers.CharField()
    

    class Meta:
        model = UserProfile
        fields = ['user']
        

class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['profile']