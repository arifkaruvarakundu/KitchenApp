from django.urls import path
from .views import UserRegistrationView, UserLoginView, RequestPasswordReset, ResetPassword, SaveAddressView, UserDetailView, UpdateUserProfileView
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name= 'login'),
    path('auth/reset_password_request/', RequestPasswordReset.as_view(), name='reset-password-request'),
    path('auth/reset_password/<uidb64>/<token>/', ResetPassword.as_view(), name='reset-password'),
    path('api/save-address/', SaveAddressView.as_view(), name='save-address'),
    path('user_details/', UserDetailView.as_view(), name='profile'),
    path('profile/update/', UpdateUserProfileView.as_view(), name='profile-update'),

]