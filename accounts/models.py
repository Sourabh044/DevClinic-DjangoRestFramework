import uuid
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser , AbstractUser)
from .manager import UserManager
from django.conf import settings
# from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
# from django.db.models.signals  import post_save , post_init
from django.conf import settings
# Create your models here.

GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
)


Dr_List = (
    ("Dr. LIM", "Dr. LIM"),
    ("Dr. Meledez", "Dr. Meledez"),
)


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    def random_otp():
        import random
        return str(random.randint(1000,9999))

    name = models.CharField(max_length=36)
    is_verified = models.BooleanField(default=False)
    otp = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    mobile = models.CharField(max_length=14)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','mobile']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin



# @receiver(post_save, sender=User)
# def send_email_token(sender, instance , created, **kwargs):
#     try:
#         # otp = random.randint(1000,9999)
#         # instance.otp = otp
#         # print(instance.otp)
#         subject = 'Your Email Needs to be verified'
#         message = f'Hi your otp to register is {instance.otp}'
#         print(message)
#         # message = f'Hi, Here on the link to verify mail http://127.0.0.1:8000/signup/verify/{uuid.uuid4()}/'
#         email_from = settings.EMAIL_HOST_USER  
#         recipient_list = [instance.email]
#         # send_mail(subject, message,email_from, recipient_list)
#     except Exception as e:
#         print(e)





# class User(AbstractUser):
#     username = None
#     email = models.EmailField(unique=True, verbose_name="Email Address")
#     mobile = models.CharField(max_length=14)
#     email_token = models.CharField(max_length=100, null=True,blank=True)
#     forgot_password = models.CharField(max_length=100, null=True,blank=True)
#     is_verified = models.BooleanField(default=False)
#     objects = UserManager()

#     USERNAME_FIELD = 'email'

#     REQUIRED_FIELDS = []


class Patient(models.Model):
    # settings.AUTH_USER_MODEL
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=200,null=False, blank=False)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES,null=False, blank=False)
    phone = models.CharField(max_length=200,null=False, blank=False)
    email = models.EmailField(max_length=200,null=False, blank=False)
    date_recorded = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Appointment(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    name = models.CharField(default= patient.name ,max_length=100, null=True)
    uid = models.UUIDField( default = uuid.uuid4 ,unique=True, primary_key=True , editable=False)
    description = models.TextField(null=False,blank=False)
    date_requested = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    Dr_Name = models.CharField(max_length=200, choices=Dr_List , default=" ", blank=False)
    created = models.DateTimeField(auto_now_add=True)
  # updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.patient.name