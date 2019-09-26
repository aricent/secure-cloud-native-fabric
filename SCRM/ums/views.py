# 
#  Copyright 2019 Altran. All rights reserved.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# 
# 
"""
This views module we have used for
Login/Logout/signup/List/Update/Retrieve/Delete
"""
import logging

from django.utils.translation import gettext as _
from django.contrib.auth import authenticate
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render

from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import list_route

from .lib.utils.auto_schema import CustomAutoSchema
from .models import ScfUser
from .serializers import (LoginSerializer,
                          SessionSerializer,
                          SignupSerializer,
                          UserSerializer,
                          UserShortSerializer,
                          UserPasswordResetSerializer)

from .filters import UserFilter
from .exceptions import HasDependents

security_logger = logging.getLogger(__name__)

def scf_login(request):
    return render(request, '../templates/login.html', None)

def scf_signup(request):
    return render(request, '../templates/signup.html', None)

class Login(generics.GenericAPIView):
    """ Login with Allow any anonymous user permission"""
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        """ Login with http method post"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            user = authenticate(email=email, password=password)
            security_logger.info("user login with email : {} and password : {} "
                                 .format(email, password))
            if user:
                if user.is_active:
                    request.user = user
                    serializer = SessionSerializer(user, context={'request': request})
                    return Response(serializer.data)
                else:
                    content = {'detail': _('User account not active.')}
                    return Response(content, status=status.HTTP_401_UNAUTHORIZED)
            else:
                content = {'detail': _('Unable to login with provided credentials.')}
                return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    """ Logout if user authenticated"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Remove all auth tokens owned by request.user
        """

        tokens = Token.objects.filter(user=request.user)
        for token in tokens:
            token.delete()
        content = {'sucess': 'User logged out.'}
        security_logger.debug("User logged out.........")
        return Response(content, status=status.HTTP_200_OK)


class Signup(generics.GenericAPIView):
    """ Signup with Allow any anonymous"""
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    def post(self, request):
        """ Signup with http method post"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                ScfUser.objects.get(email=request.data['email'])
                content = {'detail': 'User with this Email address already exists.'}
                return Response(content, status=status.HTTP_409_CONFLICT)
            except ScfUser.DoesNotExist:
                user_data = serializer.data
                user_data['is_active'] = True
                user_data['last_login'] = timezone.now()
                user = ScfUser.objects.create(**user_data)
                # if 'password' in serializer.data:
                user.set_password(serializer.data['password'])
                user.save()
                # content = {'detail': ' Your registration information has been submitted.'}
                request.user = user
                serializer = SessionSerializer(user, context={'request': request})
                return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.

    """
    model = ScfUser
    serializer_class = UserSerializer
    queryset = ScfUser.objects.all()
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = UserFilter
    ordering_fields = ('last_name', 'first_name', 'email', 'is_active')
    ordering = ('last_name', 'first_name')
    permission_classes = (IsAuthenticated,)
    schema = CustomAutoSchema()
    http_method_names = ['get', 'post', 'put', 'delete']
    serializers = {
        'default': UserSerializer,
        'list': UserShortSerializer,
        'password': UserPasswordResetSerializer
    }

    def get_serializer_class(self):
        """override serializer class object"""
        return self.serializers.get(self.action, self.serializers['default'])

    def get_serializer_context(self):
        """get request context"""
        return {'request': self.request}

    def destroy(self, request, pk=None):
        """
        Deletes a user.  Access: Super Admin  Notes:
        User cannot be deleted if they are associated
        with objects and/or activities within the system.
        """
        user = self.get_object()
        try:
            user.is_active = False
            user.save()
            security_logger.info("User is Deactivated.........")
        except HasDependents:
            name = user.get_full_name()
            message = ('%s cannot be deleted because this user is associated '
                       'with objects and/or activities that are currently '
                       'present in the system. Please set the user to '
                       '"inactive" instead. Once user is set inactive, '
                       'the system will preserve their contributions but user '
                       'will not be able to access the system.' % name)
            return Response({'status': 'danger', 'message': message},
                            status=status.HTTP_409_CONFLICT)
        return Response({'message': "User successfully deactivated."},
                        status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
    # def retrieve(self, request, pk):
        """
        Returns the user with specified id.
        """
        security_logger.info("retrieve user details.........")
        return super(UserViewSet, self).retrieve(self, request, pk)

    def update(self, request, *args, **kwargs):
        """
        Updates the user with the specified id.  Access: Self or Super Admin
        """
        try:
            super(UserViewSet, self).update(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'status': 'warning', 'message': 'Could not update user. {msg}'.format(msg=e.msg)},
                status=status.HTTP_200_OK)
        security_logger.info("update user.........")
        return Response(
            {'status': 'success', 'message': 'Profile changes were successfully saved'},
            status=status.HTTP_200_OK)

    def list(self, request):
        """
        Returns a list of users.<br>
        --
        ordering - parameter to specify the result ordering: last_name, first_name,
        email, is_active, Use the minus sign to specify descending order.
        Multiple parameters should be separated with a comma. E.g first_name,last_name
        """
        # If status is unspecified, defaults to active users
        security_logger.info("get users list.........................")
        if self.request.query_params.get('status', None) is None:
            self.queryset = self.queryset.filter(is_active=True)
        return super(UserViewSet, self).list(request)

    @list_route(methods=['post'], permission_classes=[])
    def password(self, request):
        """
        Resets a user's password.<br>
        Required parameters: email,oldPassword, newPassword, newPasswordConfirm<br>
        Optional parameters: None<br>

        To change an existing known password, supply the password details: <br>
        oldPassword, newPassword, newPasswordConfirm
        """
        permission_denied_str = 'You do not have permission to perform this action.'

        def _change_password(user, old_password, new_password):
            security_logger.info("user change password.........")
            if request.user == user:
                if authenticate(email=user.email, password=old_password):
                    user.set_password(new_password)
                    user.save()
                    return Response({"detail": "Password was successfully updated."})
                else:
                    return Response({"detail": "Old password was incorrect."},
                                    status=status.HTTP_401_UNAUTHORIZED)
            else:
                raise PermissionDenied(permission_denied_str)

        serializer = self.get_serializer_class()(data=request.data)
        if not serializer.is_valid():
            raise ParseError(serializer.errors)

        validated_data = serializer.validated_data
        email = validated_data.get('email')
        user = ScfUser.objects.get(email=email)
        old_password = validated_data.get('oldPassword')
        new_password = validated_data.get('newPassword')
        return _change_password(user, old_password, new_password)
