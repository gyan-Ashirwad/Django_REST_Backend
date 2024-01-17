from django.urls import path
from myapp.views import RegisterUserView, UserLoginView, AllUsersView, UserDetailView, SearchAPIView, UserProfileView,TwilioSendSMS, check_twilio_messages

urlpatterns = [
    # path('register/',RegisterView.as_view(),name='register'),
    path('register/',RegisterUserView.as_view(),name='register'),
    path('login/', UserLoginView.as_view(), name='auth_login'),
    path('deleteuser/<int:pk>',AllUsersView.as_view(),name='delete'),
    path('allusers/',AllUsersView.as_view(),name='allget'),
    path('allusers/<int:pk>',UserDetailView.as_view(),name='allget'),
    path('search/', SearchAPIView.as_view(), name='search_api'),
    path('profile/',UserProfileView.as_view(),name='profile'),
    path('send-sms/', TwilioSendSMS.as_view(), name='send-sms'),
    # path('sms', TwilioWebhook.as_view(), name='twilio-webhook'),
    path('check-twilio-messages/', check_twilio_messages.as_view(), name='check-twilio-messages'),

    
    
]