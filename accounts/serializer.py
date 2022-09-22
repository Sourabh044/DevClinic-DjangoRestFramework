from dataclasses import field
from datetime import tzinfo
import email
from random import random
import re
from xml.dom import ValidationErr
from rest_framework import serializers

from accounts.utils import send_email_token, send_reset_otp
from .models import Patient , Appointment , User
from django.template.defaultfilters import slugify

# All User Serialiezers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','mobile', 'name']

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','mobile', 'name','password','otp']
        extra_kwargs={
            'password':{'write_only':True},
            'otp': {'write_only':True}
        }
        
class UserVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['otp','is_verified']
        extra_kwargs = {
            'otp':{'write_only':True}
        }

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']

class UserPasswordChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']
        extra_kwargs={
            'password':{'write_only':True},
        }

class UserPasswordResetMailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:        
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            import random
            new = random.randint(1000,9999)
            print('initial OTP',user.otp)
            user.otp = new
            print('New OTP',user.otp)
            print('initial update time',user.updated_at)
            send_reset_otp(user.otp,email)
            user.save()
            print('after update time',user.updated_at)
        else:
            raise ValidationErr("You Are not a registered user")
        return attrs
class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:        
        fields = ['email','password']
        # extra_kwargs={
        #     'password':{'write_only':True}
        # }

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_verified:
                raise ValidationErr('You are already verified')
            import random
            new = random.randint(1000,9999)
            print('initial OTP',user.otp)
            user.otp = new
            send_reset_otp(new,email)
            print('New OTP',user.otp)
            user.save()
        else:
            raise ValidationErr("You Are not a registered user")
        return attrs
        
# Patient's Serializer

class PatientSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # added_by = serializers.CharField(default=serializers.CurrentUserDefault())
    slug = serializers.SerializerMethodField()
    class Meta:
        model = Patient
        exclude = ['date_recorded']

    def get_slug(self, obj):
        return slugify(obj.name)

    def validate_name(self,data):
        if data:
            name = data
            regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
            if not (regex.search(name) == None):
                raise serializers.ValidationError('Name can\'t have special characters.')

        return data

    # def validate(self, validated_data):
    #     if validated_data.get('name'):
    #         name = validated_data['name']
    #         regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
    #         if not (regex.search(name) == None):
    #             raise serializers.ValidationError('Name can\'t have special characters.')

    #     return validated_data


# Appointment Serializer
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def create(self, validated_data):
        patientid = validated_data['patient']
        print(patientid)
        # patient = Patient.objects.get(id=patientid)
        # print(patient)
        validated_data['name'] = patientid
        return super().create(validated_data)