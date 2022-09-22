from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail


def send_email_token(otp,email):
    try:
        # print('inside utils')
        subject = 'Your Email Verification Code.'
        message = f'Hi your otp to register is {otp}'
        print(message)
        email_from = settings.EMAIL_HOST_USER  
        recipient_list = [email]
        # subject = f'Your OTP for Registration is {otp}'
        send_mail(subject, message,email_from, recipient_list)
    except Exception as e:
        print(e)

def send_reset_otp(otp,email):
    try:
        subject = 'Your Email Verification Code.'
        message = f'Hi your otp to Reset Password is {otp}'
        print(message)
        email_from = settings.EMAIL_HOST_USER  
        recipient_list = [email]
        # subject = f'Your OTP for Registration is {otp}'
        send_mail(subject, message,email_from, recipient_list)
    except Exception as e:
        print(e)
