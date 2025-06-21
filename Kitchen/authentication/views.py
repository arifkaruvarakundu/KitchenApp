import os
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .serializers import *
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
from rest_framework.generics import RetrieveAPIView
import traceback
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
# from rest_framework.permissions import IsAdminUser

# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# User Registration View
class UserRegistrationView(APIView):
    """
    API View to handle user registration.

    Allows any user (authenticated or not) to send a POST request to register a new account.
    If the provided data is valid, a new user is created, and a JWT token is returned.
    If invalid, it returns appropriate error messages.

    Permissions:
        - AllowAny: No authentication required.

    Methods:
        - POST: Accepts user data and creates a new user account.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles POST requests for user registration.

        Expects:
            - email: User's email address (required)
            - password: User's password (required)
            - (any other fields defined in the serializer)

        Returns:
            - 201 Created: If registration is successful, returns JWT token and user email.
            - 400 Bad Request: If validation fails, returns serializer error details.
        """
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)

            return Response(
                {
                    'token': token,
                    'email': user.email,
                    'msg': 'Registration Success'
                },
                status=status.HTTP_201_CREATED
            )

        # Debug log for serializer validation errors (consider using proper logging in production)
        print("Validation error:", serializer.errors)

        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    

# User Registration View
class AdminUserRegistrationView(APIView):
    """
    API View to handle user registration.

    Allows any user (authenticated or not) to send a POST request to register a new account.
    If the provided data is valid, a new user is created, and a JWT token is returned.
    If invalid, it returns appropriate error messages.

    Permissions:
        - AllowAny: No authentication required.

    Methods:
        - POST: Accepts user data and creates a new user account.
    """
    permission_classes = [AllowAny]

    def post(self, request):

        print("@@################",request.data)
        """
        Handles POST requests for user registration.

        Expects:
            - email: User's email address (required)
            - password: User's password (required)
            - (any other fields defined in the serializer)

        Returns:
            - 201 Created: If registration is successful, returns JWT token and user email.
            - 400 Bad Request: If validation fails, returns serializer error details.
        """
        serializer = AdminUserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)

            return Response(
                {
                    'token': token,
                    'email': user.email,
                    'msg': 'Registration Success'
                },
                status=status.HTTP_201_CREATED
            )

        # Debug log for serializer validation errors (consider using proper logging in production)
        print("Validation error:", serializer.errors)

        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# User Login View
class UserLoginView(APIView):
    """
    API View to handle user login.

    Allows any user (authenticated or not) to send a POST request with valid credentials
    to obtain a JWT token for authenticated access. Returns user details upon successful login.

    Permissions:
        - AllowAny: No authentication required.

    Methods:
        - POST: Accepts email and password for user authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles POST requests for user login.

        Expects:
            - email: User's email address (required)
            - password: User's password (required)

        Returns:
            - 200 OK: If login is successful, returns JWT token and user details.
            - 401 Unauthorized: If credentials are invalid.
        """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # Authenticate user using email and password
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
                'is_admin': user.is_admin,
                'profile_img': profile_img_url,
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Invalid email or password.'
        }, status=status.HTTP_401_UNAUTHORIZED)


# Password Reset Views

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

            mobile_url = f"myapp://reset-password/{uid}/{token}"  # Mobile deep link
            web_url = f"https://yourfrontend.com/reset-password/{uid}/{token}"  # Web fallback

            subject = "Password Reset Request"
            text_message = (
                f"Hi {user.email},\n\n"
                f"You requested a password reset. Use one of the links below:\n\n"
                f"Mobile: {mobile_url}\n"
                f"Web: {web_url}\n\n"
                "If you didn't request this, you can ignore this email."
            )

            html_message = f"""
                <p>Hi {user.email},</p>
                <p>You requested a password reset. Use the link below:</p>
                <p><a href="{mobile_url}" style="padding: 10px 20px; background-color: #58b3e4; color: white; text-decoration: none; border-radius: 5px;" target="_blank">Reset Password (Mobile)</a></p>
                <p>Or use the web version: <a href="{web_url}">Reset via Web</a></p>
                <p>If you didn't request this, you can ignore this email.</p>
            """

            email_msg = EmailMultiAlternatives(subject, text_message, to=[email])
            email_msg.attach_alternative(html_message, "text/html")
            email_msg.send()

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
        
# Save Address View
class SaveAddressView(APIView):
    """
    API View to save a user's address.

    This view allows authenticated users to submit and save a new shipping address.
    It uses a Django form (`AddressForm`) for validation.

    Permissions:
        - IsAuthenticated: Only authenticated users can access this endpoint.

    Methods:
        - POST: Accepts address data and saves it to the user's profile.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles POST requests to save a shipping address.

        Expects:
            - All fields required by AddressForm (e.g., street, city, zip, etc.)

        Returns:
            - 201 Created: If address is saved successfully.
            - 400 Bad Request: If form validation fails, returns form error details.
        """
        form = AddressForm(request.data)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.address_type = 'shipping'  # Defaulting to shipping; modify if dynamic
            address.save()

            return Response(
                {'success': 'Address saved successfully'},
                status=status.HTTP_201_CREATED
            )

        return Response(
            form.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# User Profile Detail View
class UserDetailView(APIView):
    """
    API View to retrieve the details of the authenticated user's profile.

    This view allows an authenticated user to retrieve their own profile information. 
    The user must be authenticated to access this endpoint, as enforced by the 
    IsAuthenticated permission.

    Permissions:
        - IsAuthenticated: Only accessible by authenticated users.

    Methods:
        - GET: Returns the authenticated user's profile details.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve the authenticated user's profile details.

        Expects:
            - The user must be authenticated.

        Returns:
            - 200 OK: If the user's profile is retrieved successfully.
            - 401 Unauthorized: If the user is not authenticated (handled by IsAuthenticated).
        
        Parameters:
            request (Request): The request object containing the user's authentication details.
            *args: Variable length arguments.
            **kwargs: Keyword arguments.

        Response:
            - A Response object containing the user profile data.
        """
        # The user is already authenticated as ensured by the IsAuthenticated permission
        user = request.user  # Get the authenticated user
        
        # Serialize the user profile data
        serializer = UserDetailSerializer(user, context={'request': request})
        
        # Return the profile details with a successful status
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# User Profile Update View
class UpdateUserProfileView(APIView):
    """
    API View to update the authenticated user's profile information.

    This view allows users to update their profile data, including fields like 
    first name, last name, email, profile image, and addresses. The update is 
    partial, meaning that only the provided fields in the request will be updated.

    Permissions:
        - IsAuthenticated: Only accessible by authenticated users.

    Parser Classes:
        - MultiPartParser: Supports multipart form data (e.g., file uploads).
        - FormParser: Parses form-encoded data.
        - JSONParser: Parses JSON-encoded data.

    Methods:
        - PATCH: Accepts partial profile updates.
    """
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, *args, **kwargs):
        """
        Handles PATCH requests to update the authenticated user's profile.

        Expects:
            - A JSON or multipart form containing any fields that need to be updated. 
              The request may include fields like:
                - first_name
                - last_name
                - email
                - profile_img (optional)
                - addresses (optional)

        Returns:
            - 200 OK: If the profile was successfully updated, returns a success message and the updated data.
            - 400 Bad Request: If the provided data is invalid or does not pass validation.
            - 500 Internal Server Error: If there is an error during saving the data (e.g., database issues).

        Parameters:
            request (Request): The request object containing the data to be updated.
            *args: Variable length arguments.
            **kwargs: Keyword arguments.

        Response:
            - A Response object containing the status of the update.
        """
        # Get the authenticated user from the request
        user = request.user  # Authenticated user
        
        # Initialize the serializer with the user and the incoming request data
        serializer = UserDetailSerializer(user, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            try:
                # Save the updated user profile data
                serializer.save()
                return Response({
                    'message': 'Profile updated successfully.',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                # Log the full traceback for debugging purposes
                traceback.print_exc()  
                return Response({
                    'error': f'An error occurred while saving: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If the serializer is invalid, return error details
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Profile Image Update View
class ProfileImageUpdateView(APIView):
    """
    API View to update the profile image of the authenticated user.

    Allows authenticated users to update their profile image using a PATCH request.
    The update is handled partially, meaning only the image field is required in the request.

    Permissions:
        - IsAuthenticated: Only accessible to authenticated users.

    Methods:
        - PATCH: Updates the user's profile image.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, *args, **kwargs):
        """
        Handles PATCH requests to update the user's profile image.

        Expects:
            - profile_img: Image file to update the user's profile image.

        Returns:
            - 200 OK: If the image is successfully updated.
            - 400 Bad Request: If the input data is invalid.
        """
        user = request.user
        serializer = ProfileImageSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile image updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Current User View
class CurrentUserView(RetrieveAPIView):
    """
    API View to retrieve the currently authenticated user's information.

    This view returns the details of the logged-in user using the `UserSerializer`.

    Permissions:
        - IsAuthenticated: Only accessible to authenticated users.

    Methods:
        - GET: Returns the authenticated user's data.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieves the user object associated with the current authenticated request.

        Returns:
            - User instance of the currently authenticated user.
        """
        return self.request.user

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class AdminUserDetailsView(APIView):
    """
    API View to retrieve details of a specific user by their ID.

    This view allows administrators to access detailed information about any user in the system.

    Permissions:
        - IsAdminUser: Only accessible to users with admin privileges.

    Methods:
        - GET: Returns the details of the specified user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Handles GET requests to retrieve a user's details by their ID.

        Expects:
            - user_id: The ID of the user whose details are being requested.

        Returns:
            - 200 OK: If the user is found and details are returned.
            - 404 Not Found: If the user does not exist.
        """
        try:
            user = User.objects.get(id=user_id)
            serializer = AdminUserDetailsSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

class EditUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request, id):
        user = get_object_or_404(User, pk=id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully', 'data': serializer.data})
        return Response(serializer.errors, status=400)
    
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=204)

class ChangePasswordView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({"error": "New password must be at least 8 characters."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"success": "Password updated successfully."}, status=status.HTTP_200_OK)
