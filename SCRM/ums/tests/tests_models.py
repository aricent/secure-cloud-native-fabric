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
ScfUser model testcases
"""
from django.test import TestCase

from ums.models import ScfUser


class ScfUserTest(TestCase):
    """user test cases"""
    def setUp(self):
        """ initialized setup data"""
        self.myuser = ScfUser.objects.create_user(
            email='user@example.com',
            password='password',
            first_name='first_name',
            last_name='last_name')

    def test_email_attribute(self):
        """test email attribute"""
        myuser = ScfUser.objects.get(email='user@example.com')
        self.assertEqual(myuser.email, 'user@example.com')

    def test_first_name_attribute(self):
        """test first name attribute"""
        myuser = ScfUser.objects.get(email='user@example.com')
        self.assertEqual(myuser.first_name, 'first_name')

    def test_last_name_attribute(self):
        """test last name attribute"""
        myuser = ScfUser.objects.get(email='user@example.com')
        self.assertEqual(myuser.last_name, 'last_name')

    def test_is_active_attribute(self):
        """test is_active attribute"""
        myuser = ScfUser.objects.get(email='user@example.com')
        self.assertEqual(myuser.is_active, True)

    def test_date_joined_attribute(self):
        """test date_joined attribute"""
        myuser = ScfUser.objects.get(email='user@example.com')
        self.assertEqual(myuser.date_joined, myuser.date_joined)

    def test_create_user(self):
        """test create_user attribute"""
        user = ScfUser.objects.create_user(email='user1@example.com',
                                          password='password')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_staff(self):
        """test create_staff attribute"""
        user_staff = ScfUser.objects.create_staff(email='staff@example.com',
                                                 password='password')
        self.assertTrue(user_staff.is_staff)
        self.assertFalse(user_staff.is_superuser)

    def test_create_superuser(self):
        """test create_superuser attribute"""
        superuser = ScfUser.objects.create_superuser(email='superuser@example.com',
                                                    password='password')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
