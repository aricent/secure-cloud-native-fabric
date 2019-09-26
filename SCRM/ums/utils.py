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
""" ums utils"""

from django.conf import settings

from django.core.mail import send_mail as mail


def get_app_url():
    """ here we will fetch scf url"""
    try:
        base_url = settings.SCF_URL
    except:
        print("No SCF_URL defined in settings")
        raise
    return base_url


class SCFMailException(Exception):
    """ custom mail exceptions"""
    pass


def send_mail(recipient_mail, type_mail, context=None, **kwargs):
    """ custom mail method WIP """
    if settings.SKIP_SENDING_EMAILS:
        return


    from_mail = kwargs.get('from_mail', settings.DEFAULT_FROM_EMAIL)
    base_url = get_app_url()
    use_context = {'base_url': base_url}
    if context:
        use_context.update(context)
    try:
        mail.send(
            recipient_mail,
            from_mail,
            template=type_mail,
            context=use_context)
    except Exception as e:
        raise SCFMailException(e.message)

