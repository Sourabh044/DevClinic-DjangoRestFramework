from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'patients',PatientViewSet, basename='patients')
# To delete patient just add its id after the url ends eg. http://127.0.0.1:8000/25/patients/
# To patch a patient just add the id of the patient before the url name eg. http://127.0.0.1:8000/patients/25/
# To see a singe patient details just do a get request  eg. http://127.0.0.1:8000/patients/25/ 


urlpatterns = [
    # path('post-patient/', post_patient, name='post_patient' ),
    # path('patch-patient/', patch_patient, name='patch_patient' ),
    # path('get-appointment/<str:pk>', get_appointment, name='get_appointment' ), # single appointment
    path('appointments/', AppointmentView.as_view(), name='appointments' ), #to fetch all the appointments
    # to get single appointment use get method and url is 'appointments/<str:pk>'
    path('appointments/<str:pk>/', AppointmentView.as_view(), name='delete-appointments' ), # url to delete appointment
    path('signup/', UserSignupView.as_view(), name='Create User' ),
    path('signup/verify/<str:token>/',UserVerifyView.as_view(), name='verify-User' ),
    path('login/', UserLoginView.as_view(), name='login'),
    path('login/verify/', UserVerifyView.as_view(), name='verify' ),
    path('profile/', UserProfileView.as_view(), name='profile' ),
    path('profile/changepassword/', UserPasswordChange.as_view(), name='change-password' ),
    path('profile/forgotpassword/', UserPasswordResetMail.as_view(), name='reset-password-email' ),
    path('profile/resetpassword/', UserPasswordReset.as_view(), name='reset-password' ),



]
urlpatterns += router.urls  