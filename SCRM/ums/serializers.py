""" Ums serializer's """

from rest_framework.exceptions import ParseError, ValidationError
from rest_framework import serializers
from .models import ScfUser


class LoginSerializer(serializers.Serializer):
    """ Login with email and password"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class SessionSerializer(serializers.ModelSerializer):
    """ Get fields in user login"""
    token = serializers.SerializerMethodField('get_user_token')

    class Meta:
        """get custom fields"""
        model = ScfUser
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'token')

    def get_user_token(self, obj):
        """get user instance token"""
        return obj.get_session_token()


class SignupSerializer(serializers.Serializer):
    """ Signup with mandatory fields"""
    email = serializers.EmailField(max_length=255)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=150)

    def validate_username(self, data):
        """ check user name is exist or not"""
        try:
            ScfUser.objects.get(username=data)
            raise ValidationError("User {} name already exist".format(data))
        except ScfUser.DoesNotExist:
            return data

    def validate_email(self, data):
        """ check email is exist or not"""
        try:
            ScfUser.objects.get(email=data)
            raise ValidationError("User {} email already exist".format(data))
        except ScfUser.DoesNotExist:
            return data


class UserSerializer(serializers.ModelSerializer):
    """user serializer with below fields """
    token = serializers.SerializerMethodField('get_user_token')

    class Meta:
        """get custom fields"""
        model = ScfUser
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'token', 'username')

    def get_user_token(self, obj):
        """ get user token """
        return obj.get_session_token()


class UserShortSerializer(serializers.ModelSerializer):
    """ user short serializer with few or custom fields """
    name = serializers.ReadOnlyField(source='full_name')

    class Meta:
        """get custom fields"""
        model = ScfUser
        fields = ('id', 'email', 'first_name', 'is_active', 'last_name', 'name')


class UserPasswordResetSerializer(serializers.Serializer):
    """ User reset password serializer """
    email = serializers.CharField(max_length=254, required=True)
    oldPassword = serializers.CharField(max_length=128, required=True)
    newPassword = serializers.CharField(max_length=128, required=True)
    newPasswordConfirm = serializers.CharField(max_length=128, required=True)

    class Meta:
        """ get custom fields"""
        fields = ('email', 'oldPassword', 'newPassword', 'newPasswordConfirm')

    def validate_email(self, data):
        """ check email is exist or not"""
        try:
            ScfUser.objects.get(email=data)
        except:
            raise ParseError("User {} does not exist".format(data))
        return data

    def validate(self, data):
        """ validate password """
        newPassword = data.get('newPassword')
        if newPassword and newPassword != data.get('newPasswordConfirm'):
            raise ParseError("newPassword did not match newPasswordConfirm")
        return data
