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
Using this function we can easily fetch model object by giving model name
"""

from django.apps import apps


def get_model_class(model_name):
    """
    This is intended to replace all our varied ways of identifying a particular model class.
    This uses the standard django name for any model class.
    :param model_name: string of the form <app name>.<model class name>
    :return: model class
    """
    (app_label, model_class_name) = model_name.split('.')
    return apps.get_model(app_label=app_label, model_name=model_class_name)
