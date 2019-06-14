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
