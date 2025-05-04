from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                validated_token = AccessToken(access_token)
                user = JWTAuthentication().get_user(validated_token)
                request.user = user  # Set the user in request
            except Exception as e:
                print(f"JWT Middleware Error: {e}")
                request.user = None