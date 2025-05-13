from django.urls import path
from .views import UserRegistrationView, UserLoginView, RequestPasswordReset, ResetPassword, SaveAddressView, UserDetailView, UpdateUserProfileView, ProfileImageUpdateView, CurrentUserView
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name= 'login'),
    path('reset_password_request/', RequestPasswordReset.as_view(), name='reset-password-request'),
    path('reset_password_confirm/<uidb64>/<token>/', ResetPassword.as_view(), name='reset-password'),
    path('api/save-address/', SaveAddressView.as_view(), name='save-address'),
    path('user_details/', UserDetailView.as_view(), name='profile'),
    path('profile/update/', UpdateUserProfileView.as_view(), name='profile-update'),
    path('current_user/', CurrentUserView.as_view(), name='current_user'),
    path('update_profile_image/', ProfileImageUpdateView.as_view(), name='update-profile-image'),

]