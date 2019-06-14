"""
User/scf user api test cases
"""
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from ums.models import ScfUser


class UserRegistrationAPIViewTestCase(APITestCase):
    """ user registration api test cases """
    url = reverse('hav-signup')

    def test_user_registration(self):
        """
        Test to verify that a post call with user valid data
        """
        user_data = {
            "email": "test@testuser.com",
            "username": "test@testuser.com",
            "password": "123123",
            "first_name": "first_name",
            "last_name": "last_name"
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(200, response.status_code)
        self.assertTrue("token" in response.data)

    def test_unique_username_validation(self):
        """
        Test to verify that a post call with already exists username
        """
        user_data_1 = {
            "email": "test@testuser.com",
            "username": "new_test@testuser.com",
            "password": "123123",
            "first_name": "first_name",
            "last_name": "last_name"
        }
        response = self.client.post(self.url, user_data_1)
        self.assertEqual(200, response.status_code)

        user_data_2 = {
            "email": "test1@testuser.com",
            "username": "new_test@testuser.com",
            "password": "123123",
            "first_name": "first_name",
            "last_name": "last_name"
        }
        response = self.client.post(self.url, user_data_2)
        self.assertEqual(400, response.status_code)

    def test_email_username_validation(self):
        """
        Test to verify that a post call with already exists email
        """
        user_data_1 = {
            "email": "test@testuser.com",
            "username": "new_test1@testuser.com",
            "password": "123123",
            "first_name": "first_name",
            "last_name": "last_name"
        }
        response = self.client.post(self.url, user_data_1)
        self.assertEqual(200, response.status_code)

        user_data_2 = {
            "email": "test@testuser.com",
            "username": "new_test@testuser.com",
            "password": "123123",
            "first_name": "first_name",
            "last_name": "last_name"
        }
        response = self.client.post(self.url, user_data_2)
        self.assertEqual(400, response.status_code)


class UserLoginAPIViewTestCase(APITestCase):
    """ user login api test cases """
    url = reverse("hav-login")

    def setUp(self):
        """ initialized setup data"""
        self.username = "ranvijay"
        self.email = "ranvijay@example.com"
        self.password = "you_know_nothing"
        self.user = ScfUser.objects.create_user(self.email, self.password)

    def test_authentication_without_password(self):
        """ authentication without password"""
        response = self.client.post(self.url, {"email": "ranvijay@example.com"})
        self.assertEqual(400, response.status_code)

    def test_authentication_with_wrong_password(self):
        """ authentication without wrong password"""
        response = self.client.post(self.url, {"email": self.email, "password": "I_know"})
        self.assertEqual(401, response.status_code)

    def test_authentication_with_valid_data(self):
        """ authentication without valid data"""
        response = self.client.post(self.url, {"email": self.email, "password": self.password})
        self.assertEqual(200, response.status_code)
        self.assertTrue("token" in response.data)


class UserLogoutAPIViewTestCase(APITestCase):
    """ user logout api test cases """
    url = reverse("hav-logout")

    def setUp(self):
        """ initialized setup data"""
        self.username = "logout_test"
        self.email = "logout_test@example.com"
        self.password = "you_know_nothing"
        self.user = ScfUser.objects.create_user(self.email, self.password)
        self.token = Token.objects.get_or_create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        """ get client session"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token[0].key)

    def test_logout(self):
        """ test user logout"""
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertFalse(Token.objects.filter(key=self.token[0].key).exists())
