import random
from django.utils import timezone
from .models import Event
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
BrEvents
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )
def send_resend_email_otp(user, code):
    """
    Sends resend email verification OTP to user's email
    """
    subject = "Your email verification code (Resent)"

    message = f"""
Hello {user.full_name},

You requested to resend your email verification code.

Your registered email-id is {user.email}.

Your new email verification code is: {code}

This code is valid for a limited time only.

If you did not request this, please ignore this email.

Regards,
BrEvents
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )
def send_password_reset_otp(user, code):
    """
    Sends forgot-password OTP to user's email
    """
    subject = "Reset your password"

    message = f"""
Hello {user.full_name},

We received a request to reset your account password.

Your password reset OTP is: {code}

 This OTP is valid for a limited time.
If you did not request a password reset, please ignore this email.

Regards,
BrEvents
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )



def send_event_participation_email(user=None, guest_email=None, guest_name=None, event=None):
    """
    Sends event participation confirmation email
    Supports:
    - Registered users
    - Guest users
    """

    # Registered user
    if user and user.email:
        to_email = user.email
        name = user.full_name or "Participant"

    # Guest user
    elif guest_email:
        to_email = guest_email
        name = guest_name or "Participant"

    else:
        return  # no email available

    subject = f"🎉 Registration Confirmed: {event.event_name}"

    message = f"""
Dear {name},

You have been successfully registered for the event.

📌 Event Details:
------------------------
Event Name : {event.event_name}
Event Type : {event.event_type or "N/A"}
Date & Time: {event.event_date_time.strftime('%d %B %Y, %I:%M %p') if event.event_date_time else "To be announced"}
Venue      : {event.venue or "To be announced"}

We’re excited to have you join us!
Please keep an eye on your email for further updates.

Best regards,
BrEvent
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=True,
    )

def send_post_verification_event_notification(user):
    """
    Sends a "thank you for verifying" email with information about upcoming events.
    This is sent only once after the initial email verification is complete.
    """
   
    
    upcoming_events = Event.objects.filter(
        event_date_time__gte=timezone.now()
    ).order_by('event_date_time')[:3]  # Limit to next 3 events
    
    # Even if there are no events, we can send a simple "you're verified" email.
    subject = "Your BrEvents Account is Now Active!"
    
    if upcoming_events:
        # Format events list for email
        events_list = ""
        for event in upcoming_events:
            event_date = event.event_date_time.strftime('%d %B %Y, %I:%M %p') if event.event_date_time else "To be announced"
            events_list += f"""
📅 {event.event_name}
   Date & Time: {event_date}
   Venue: {event.venue or "To be announced"}
   Type: {event.event_type or "N/A"}
   {"-" * 40}
"""
        
        message = f"""
Hello {user.full_name or "User"},

Thank you for verifying your email address! Your BrEvents account is now fully active.

You're all set to explore and register for our events. Here are some upcoming opportunities you might be interested in:

{events_list}

Login to your account to secure your spot at these events or discover more.

Best regards,
The BrEvents Team
"""
    else:
        # Fallback email if there are no upcoming events
        message = f"""
Hello {user.full_name or "User"},

Thank you for verifying your email address! Your BrEvents account is now fully active.

You're all set to explore our platform. Check back soon for new and exciting events you can participate in.

Login to your account to see what's new.

Best regards,
The BrEvents Team
"""
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True, # Set to False in development to debug email issues
    )