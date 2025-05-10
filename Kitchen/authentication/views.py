import os
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserLoginSerializer, ResetPasswordRequestSerializer, ResetPasswordSerializer, UserDetailSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from django.core.mail import EmailMessage
from .forms import AddressForm
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(
                {'token' : token, 'email' : user.email, 'msg' : 'Registration Success' },
                status = status.HTTP_201_CREATED
            )
        
        else:
            print("validation error:", serializer.errors)
            return Response(
                {"errors" : serializer.errors},
                status = status.HTTP_400_BAD_REQUEST
            )

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        print("email:", type(email))
        print("password:", type(password))  

        user = authenticate(email=email, password=password)

        if user is not None:
            profile_img_url = user.profile_img.url if user.profile_img else None
            token = get_tokens_for_user(user)

            return Response({
                'token': token,
                'msg': 'Login Success',
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'profile_img': profile_img_url,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'errors': {'non_field_errors': ['Email or Password is not valid']}
            }, status=status.HTTP_401_UNAUTHORIZED)



token_generator = PasswordResetTokenGenerator()


class RequestPasswordReset(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            reset_base = os.getenv('PASSWORD_RESET_BASE_URL', 'http://127.0.0.1:8000/auth/reset-password')
            reset_url = f"{reset_base}/{uid}/{token}/"


            subject = "Password Reset Request"
            message = f"""
            Hi {user.email},
            
            You requested a password reset. Click the link below to reset your password:

            {reset_url}

            If you didn't request this, you can ignore this email.
            """
            email_msg = EmailMessage(subject, message, to=[email])
            email_msg.send()

        # Don't reveal whether the email exists
        return Response({'success': 'If the email is registered, a reset link has been sent.'}, status=status.HTTP_200_OK)


class ResetPassword(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Invalid or expired reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        if data['new_password'] != data['confirm_password']:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data['new_password'])
        user.save()

        return Response({'success': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        
class SaveAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = AddressForm(request.data)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.address_type = 'shipping'  # or 'billing' if needed
            address.save()
            return Response({'success': 'Address saved successfully'}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CurrentUserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        })

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve authenticated user's profile details.
        """
        user = request.user  # Already guaranteed to be authenticated by IsAuthenticated

        serializer = UserDetailSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateUserProfileView(APIView):
    """
    View to update the authenticated user's profile.
    Supports partial updates with JSON, Form, or Multipart data.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, *args, **kwargs):
        user = request.user  # Authenticated user

        serializer = UserDetailSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Profile updated successfully.',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': f'An error occurred while saving: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)