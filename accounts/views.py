from datetime import date, datetime , timedelta
from random import Random
from time import time
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from accounts.models import Appointment, Patient
from accounts.renderers import UserRenderer
from accounts.utils import send_email_token, send_reset_otp
from .serializer import *
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User = get_user_model()
# Generating token Manually

def otpexpire(user):
    time = datetime.now().astimezone()-user.updated_at.astimezone()
    total_seconds = time.total_seconds() 
    minutes = total_seconds/60
    print(minutes)
    if(minutes>5):
        return True
    else:
        return False

def genOtp(user):
    import random
    user.otp = random.randint(1000,9999)
    print(user.otp)
    user.save()
    return user.otp

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your views here.

# All User Views Here.  
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        try:
            if serializer.is_valid():
                email = serializer.data.get('email')
                password = serializer.data.get('password')
                user = authenticate(email=email, password=password)
                if user is not None:
                    token = get_tokens_for_user(user)
                    if not user.is_verified:
                        print('Updated_at',user.updated_at.astimezone(),'\nTime now',datetime.now().astimezone())
                        if otpexpire(user):
                            otp = genOtp(user)
                            send_email_token(user.otp,user.email)
                            return Response({
                                'status' :False,
                                'info': 'OTP Expired',
                                'msg': 'Request OTP',
                                'token': token
                            })
                        import random
                        otp = genOtp(user)
                        send_email_token(user.otp,user.email)
                        return Response({
                        'status': True,
                        'info': 'Verify_user',
                        'msg':'An otp send to your registered email.',
                        'is_verified': user.is_verified,
                        'token': token
                    })
                    return Response({
                        'status': True,
                        'message': 'login Successfully',
                        'is_verified': user.is_verified,
                        'token': token
                    })
            return Response({
                'status': False,
                'message': 'Invalid username and password'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': "something went wrong"
            }, status=status.HTTP_400_BAD_REQUEST)


class UserSignupView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        try:
            if not request.user.is_anonymous:
                return Response({
                    'error': False,
                    'message': "Not Allowed"
                }, status=status.HTTP_401_UNAUTHORIZED)
            # print(request.user)
            data = request.data
            import random
            data['otp'] = random.randint(1000,9999)
            # print(data)
            serializer = UserSignupSerializer(data=data)
            if serializer.is_valid():
                password = serializer.validated_data.get('password')
                # print('serializer data', serializer.validated_data)
                serializer.validated_data['password'] = make_password(password)
                send_email_token(data['otp'],data['email'])
                user = serializer.save()
                token = get_tokens_for_user(user)

                return Response({
                    'status': True,
                    'message': "User Created",
                   'token': token
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': False,
                'message': "Invalid data",
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': "something went wrong"
            }, status=status.HTTP_400_BAD_REQUEST)

class UserVerifyView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        id = request.user.id
        user = User.objects.get(id=id)
        if user.is_verified==True:
            otp = genOtp(user)
            print('newotp',otp)
            return Response({
                'status': False,
                'msg': 'already verified'
            })
        data = request.data
        try:
            try:
                print(user,'initial otp:',user.otp)
                dataotp = (data['otp'])
                print(type(dataotp['otp']))
                if int(dataotp['otp']) == user.otp:
                        if otpexpire(user):
                            otp = genOtp(user)
                            send_email_token(user.otp,user.email)
                            return Response({
                                'status' :False,
                                'info': 'OTP Expired',
                                'msg': 'Request OTP',
                            })                            
                        otp = genOtp(user)
                        data['is_verified'] = True
                        data['otp'] = otp
                        serializer = UserVerifySerializer(user,data=data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        print(serializer.validated_data.get('otp'))
                        print('updating user')
                        serializer.save()
                        return Response({
                        'msg' : 'bhai tera otp match hogya',
                        "status": True
                        })
                else:
                    return Response({
                        'status' : False,
                        'msg' : 'Invalid OTP'
                    })
            except Exception as e:
                return Response({
                'status' : False,
                'mag':e
                })
        except Exception as e:
            print(e)
            return Response({
            'status' : False,
            'error':e
        })

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pcount = Patient.objects.filter(user=self.request.user).count()
        acount = Appointment.objects.filter(created_by=request.user).count()
        serializer = UserSerializer(request.user)

        # serializer.is_valid(raise_exception=True)
        # print(serializer.validated_data)
        return Response({
            'status':True,
            'patients': pcount,
            'appoinments':acount,
            "msg":serializer.data,
            'verification':request.user.is_verified
        })

class UserPasswordChange(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]
    def post(self,request):
        data = request.data
        id = request.user.id
        if 'password' in data:
            user = User.objects.get(id=id)
            print(user)
            if not user.is_verified:
                return Response({
                    'status' : False,
                    'msg': 'User is not verified',
                },status=status.HTTP_400_BAD_REQUEST)
            serializer = UserPasswordChangeSerializer(user,data=data,partial=True)
            serializer.is_valid(raise_exception=True)
            password = serializer.validated_data.get('password')
            print('serializer data', serializer.validated_data)
            serializer.validated_data['password'] = make_password(password)
            user = serializer.save()
            return Response({
                'status' : True,
                'msg': 'User Password has changed.'           
            })
        return Response({
            'status': False,
            "msg":'provide password'
        })

class UserPasswordResetMail(APIView):
    renderer_classes = [UserRenderer]

    def post(self,request):
        try:
            serializer = UserPasswordResetMailSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                return Response({
                    'msg':'An Email Has been sent on your email'
                })
        except Exception as e:
            return Response({
                'msg':'error occured',
                'errors': e
            })

class UserPasswordReset(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request):
        data = request.data
        email = request.data['email']
        user = User.objects.get(email=email)
        if 'otp' in data:
            try:
                if int(data['otp']) == user.otp:
                    user.password = make_password(data['password'])
                    otp = genOtp(user)
                    # import random
                    # user.otp = random.randint(1000,9999)
                    # user.save()
                    return Response({
                        'status' : True,
                        'msg': 'New Password Set.'           
                    })
                return Response({
                    'status' : False,
                    'msg': 'Invalid OTP'
                })
            except Exception as e:
                    print(e)
                    return Response({
                    'status' : False,
                    'msg': e
                })
        return Response({
            'status' : False,
            'msg': 'Provide OTP'
        })




# Patient View Here.
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get_queryset(self):
        queryset = super().get_queryset()
        # self.request.user
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        count = Patient.objects.filter(user=self.request.user).count()
        return Response({
            'count': count,
            "Patients": serializer.data,
        })


# Old basic Crud of the Patients

# Read
@api_view(['GET'])
def get_patient(request):
    try:

        patients = Patient.objects.filter(user=request.user)
        serializer = PatientSerializer()
        serializer()
        return Response({
            'status': True,
            'message': "Fetched All Patients",
            'data': serializer.data
        })

    except Exception as e:
        print(e)
        return Response({
            'status': False,
            'message': "something went wrong"
        })

# Create
@api_view(['POST'])
def post_patient(request):
    try:
        data = request.data
        # request.user.id
        data['user'] = request.user.id
        print(request.data['user'])
        serializer = PatientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'message': "Patient Added",
                'data': serializer.data
            })
        return Response({
            'status': False,
            'message': "Invalid data",
            'error': serializer.errors
        })

    except Exception as e:
        print(e)
        return Response({
            'status': False,
            'message': "something went wrong"
        })

# Update
@api_view(['PATCH'])
def patch_patient(request):
    try:
        data = request.data
        if not id:
            return Response({
                'status': False,
                'message': "Need uid"
            })
        patient = Patient.objects.get(id=data.get('id'))
        serializer = PatientSerializer(patient, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'message': "Patient Updated",
                'data': serializer.data
            })

        return Response({
            'status': False,
            'message': "Patient Updated",
            'data': serializer.errors
        })
    except Exception as e:
        print(e)
        return Response({
            'status': False,
            'errors': e
        })


# All appointments views.

class AppointmentView(APIView):

    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #   Create Appointments
    def post(self, request):
        data = request.data
        data['created_by'] = request.user.id
        try:
            serializer = AppointmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': True,
                    'message': "Appointment Added",
                    'data': serializer.data
                })
            return Response({
                'status': False,
                'message': "Invalid data",
                'error': serializer.errors
            })
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': "Something went wrong",
                'error': e
            })

    def delete(self, request, pk):
        try:
            appointment = Appointment.objects.get(uid=pk)
            if appointment.created_by != request.user:  # Checked whether the user has created the appointment or not
                return Response({
                    'status': False,
                    'message': "Not Allowed"})
            appointment.delete()
            return Response({
                'status': True,
                'message': "deleted."
            })
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': "Something went wrong",
                'error': e
            })

    def get(self, request,pk=None):
        if 'pk' in self.kwargs:
            try:
                appointment = Appointment.objects.get(uid=self.kwargs['pk'])
                serializer = AppointmentSerializer(appointment)

                return Response({
                    'status': True,
                    'appointments': serializer.data
                })
            except Exception as e:
                print(e)
                return Response({
                    'status': False,
                    'message': "Something went wrong",
                    'error': e
                })
        user = request.user.id
        try:
            appointments = Appointment.objects.filter(created_by=user)
            acount = Appointment.objects.filter(created_by=user).count()
            serializer = AppointmentSerializer(appointments, many=True)

            return Response({
                'status': True,
                'count': acount,
                'appointments': serializer.data
            })
        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': "Something went wrong",
                'error': e
            })


# Here we can create a single view for all the methods and then check whether a method is which and proceed accordingly.
@api_view(['GET']) # we can add the ['POST',"PUT","PATCH", "DELETE"]
def get_appointment(request, pk):
    try:
        appointment = Appointment.objects.get(uid=pk)
        # print(appointment.created_by)
        # print(request.user)
        if appointment.created_by != request.user:  # Checked whether the user has created the appointment or not
            return Response({
                'error': False,
                'message': "Not Allowed"
            })
        serializer = AppointmentSerializer(appointment, many=False)
        return Response({
            'status': True,
            'data': serializer.data
        })
    except Exception as e:
        print(e)
        return Response({
            'error': False,
            'message': "something went wrong"
        }, status=status.HTTP_400_BAD_REQUEST)



