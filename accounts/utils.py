from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_email(request, user, subject, template, redirect_url):
    """
    Sends an email to the user with a custom message.
    :param request: HttpRequest object.
    :param user: User instance to whom the email is sent.
    :param subject: Subject of the email.
    :param template: Path to the template used for the email body.
    :param redirect_url: URL to redirect to after sending the email.
    """
    current_site = get_current_site(request)
    message = render_to_string(
        template,
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    email = EmailMessage(subject, message, to=[user.email])
    email.send()
