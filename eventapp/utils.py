import random

def generate_verification_code():
    return str(random.randint(100000, 999999))

from django.core.mail import send_mail
from django.conf import settings


def send_email_verification_code(user, code):
    """
    Sends email verification code to user's email
    """
    subject = "Verify your email address"

    message = f"""
Hello {user.full_name},

Thank you for registering with us.
Your registered email-id is {user.email}.

Your email verification code is: {code}

Regards
Xyz
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )
