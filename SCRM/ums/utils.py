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

