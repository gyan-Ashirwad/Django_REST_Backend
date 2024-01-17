from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser as User, UserProfile
from rest_framework import status
from .serializers import UserSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, UserLoginSerializer, UserProfileSerializer, UpdateProfileSerializer

from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        existing_user = User.objects.filter(username=request.data.get('username')).first()
        if not existing_user:
            if serializer.is_valid(raise_exception=True):
                    user = User.objects.create(
                        email=request.data.get('email'),
                        username=request.data.get('username'),
                        first_name=request.data.get('first_name'),
                        last_name=request.data.get('last_name'),
                        mobile_no=request.data.get('mobile_no'),
                        is_active=True,
                        is_admin=False,
                    )
                    user.set_password(request.data.get('password'))
                    user.save()
                    serializer.save()
                    context = serializer.data
                    
                    return Response(context, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            context= {"msg":"Username already exists"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


    
class UserLoginView(generics.CreateAPIView):

    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            username = request.data.get("username", None)
            password = request.data.get("password", None)
            try:
                user = User.objects.get(username=username)
            except Exception as e:
                print("🚀 ~ file: views.py:79 ~ e:", e)
                return Response({"error": 'User Does not Exists', 'status_code': 401,}, status=401)
                # return Response({"error": "Your username/username is not correct. Please try again or register your details"})
            if user:
                user = authenticate(username=username, password=password)
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    update_last_login(None, user)
                    response = {
                        'success': 'True',
                        'status_code': status.HTTP_200_OK,
                        'message': 'User logged in successfully',
                        'token': str(refresh.access_token),
                        'user':UserSerializer(user).data,
                    }
                    status_code = status.HTTP_200_OK
                    return Response(response, status=status_code)
                else:
                    return Response({"error": 'Your password is not correct please try again or reset your password', 'status_code': 401,}, status=401)
            else:
                return Response({"error": 'User Doesnot Exists'}, status=401)
    
    
class Searchpagination(PageNumberPagination):
    page_size = 5
    
    def get_paginated_response(self, data):
        return Response({
            'page_size': self.page_size,
            'total_objects': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page_number': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
    
    
    
class AllUsersView(APIView):
    pagination_class = Searchpagination
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]
    
    
    def get(self, request, format=None, *args, **kwargs):
        instance = User.objects.all()
        
        paginator = Searchpagination()
        context = paginator.paginate_queryset(instance, request)
        serializer = self.serializer_class(context, many=True)
        return paginator.get_paginated_response({"data": serializer.data, "status": status.HTTP_200_OK})
        
    
    def delete(self,request,pk):
        user = User.objects.get(id=pk)
        user.delete()
        return Response({"result":"user delete"})
    
   
        
class UserDetailView(APIView):
    
    def get(self, request, pk=None):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def put(self, request, pk=None):
        """ For updating an existing post, HTTP method: PUT """
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
        
        
class SearchAPIView(APIView):
    pagination_class = Searchpagination
    
    def get(self, request):
        search_query = request.query_params.get('q')
        results = User.objects.filter(Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query))
        paginator = Searchpagination()
        context = paginator.paginate_queryset(results, request)
        serializer = UserSerializer(context, many=True)
        return paginator.get_paginated_response({"data": serializer.data, "status": status.HTTP_200_OK})
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    # def get(self, request):
    #     print("======================", request.user.id)
    #     try:
    #         user = UserProfile.objects.get(user=request.user)
    #         # print("================:",user)
    #         serializer = UserProfileSerializer(user)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except UserProfile.DoesNotExist:
    #         return Response("Profile Not Exist",status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UpdateProfileSerializer(user_profile, data=request.data,  partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# twilio_app/views.py
    
#Recovery code:- 48A64BK2U6WBKZ6JHN7CXQ3S

from twilio.rest import Client
from django.conf import settings
from twilio.twiml.messaging_response import MessagingResponse
from django.http import HttpResponse



class TwilioSendSMS(APIView):
    def post(self, request, *args, **kwargs):
        to_number = request.data.get('to_number')
        print(">>>>>>>>>>>>>>>>>>>>>>",to_number)
        message_body = request.data.get('message_body')

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        
        twillo_messages = client.messages.list(from_=settings.TWILIO_PHONE_NUMBER)
        print("twillo_messages:>>>>>>>>>>>>>", twillo_messages)

        return Response({'status': 'Message sent successfully', 'message_id': message.sid})

# class TwilioWebhook(APIView):
#     def post(self, request, *args, **kwargs):
#         incoming_message = request.data.get('Body', '')
#         from_number = request.data.get('From', '')
#         print(">>>>>>>>>>????????????????????????",incoming_message)
#         print(">>>>>>>>>>>>>>>>>>>>>>>>>",from_number)
#         print(">>>>>>>>>>>>>><<<<<<<<<<<<<<<<",request.data)

#         # Handle the incoming message as needed
#         # You can save it to the database, trigger a specific action, etc.

#         # For simplicity, let's just send a response for now
#         response = MessagingResponse()
#         response.message(f"Thanks for your message, {from_number}! You said: {incoming_message}")

#         return HttpResponse(str(response))


class check_twilio_messages(APIView): 
    def post(self,request):
        account_sid = 'your_account_sid'
        auth_token = 'your_auth_token'
        twilio_number = 'your_twilio_phone_number'

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Fetch messages from Twilio
        messages = client.messages.list()

        # Process the messages as needed
        message_data = [
            {'from': message.from_, 'body': message.body, 'direction':message.direction}
            for message in messages
        ]
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>",message_data)

        return Response({'messages': message_data})