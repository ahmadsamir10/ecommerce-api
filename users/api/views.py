import uuid
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from users.models import User, Wishlist, Activation
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from .permissions import StaffNotAllowed
from .serializers import (  
                            ReviewSerializer,
                            RegisterSerializer,
                            UserAddressSerializer,
                            UserProfileSerializer,
                            ChangePasswordSerializer,
                            AccountDetailsSerializer,
                            WishlistSerializer
                        )


 
# signup view for new users
class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        #user data
        email = serializer.data.get('email')
        username = serializer.data.get('username')
        user = User.objects.get(username=username)
        
        # token
        token = str(uuid.uuid4())[:8]
        Activation.objects.create(user=user, token=token)
        
        #current site
        current_site = get_current_site(request).domain
        
        plaintext = get_template('email.txt')
        htmly     = get_template('email.html')

        context = { 'token': token, 'domain':current_site}

        subject, from_email, to = 'Welcome', 'ecommerce@mail.com', email
        text_content = plaintext.render(context)
        html_content = htmly.render(context)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        response = {'created' : 'Your account created successfully .. check mail inbox to activate it'}
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.is_staff == False:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key
            })
            
        else:
            return Response({'response':'Staff users not allowed'}, status=status.HTTP_400_BAD_REQUEST)



class ActivateAccountView(APIView):
    def get(self, request, token):
        
        try:
            activation = Activation.objects.get(token=token)
        except Activation.DoesNotExist:
            activation = None
            
        if activation is not None:
            activation.user.is_active = True
            activation.user.save()
            token = Token.objects.create(user=activation.user).key
            activation.delete()
            
            data={'activated':True, 'token':token}
            return Response(data)
        else:
            data={'activated':False, 'status':'invalid token'}
            return Response(data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({'response':'Successfully logout'}, status=status.HTTP_200_OK)
 


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, StaffNotAllowed]
    
    def get_object(self, queryset=None):
        return self.request.user
        
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # check old password 
            if not user.check_password(serializer.data.get('old_password')):
                response = {'old_password':'your old password was entered incorrectly'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            response = {'response' : 'Password updated successfully'}
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountDetailsView(UpdateAPIView):
    serializer_class = AccountDetailsSerializer
    permission_classes = [IsAuthenticated, StaffNotAllowed]
    
    def get_object(self, queryset=None):
        return self.request.user
    
    
class UserAddressView(ModelViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated, StaffNotAllowed]
    
    def get_queryset(self):
        return self.request.user.address.all()
    
    
class ListCreateUserWishlist(ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated, StaffNotAllowed]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Wishlist.objects.filter(user=user)
        return queryset
    

class CreateProductReview(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, StaffNotAllowed]
    

class MyProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, StaffNotAllowed]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        user = self.request.user
        return user
    
