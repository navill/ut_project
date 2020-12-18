from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import datetime_to_epoch

User = get_user_model()


# def update_last_logout(user):
#     user.last_logout = timezone.now()
#     user.is_logged_out = True
#     user.save()


class CustomJWTTokenUserAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user, validated_token = super().authenticate(request)
        if user.token_expired != validated_token.payload['exp']:
            raise AuthenticationFailed('User do not have valid token', code='user_without_token')

        return user, validated_token

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        return user


class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        expired = int(token.access_token.payload['exp'])
        user.set_token_expired(expired)
        return token

    def set_exp(self, claim='exp', from_time=None, lifetime=None):
        # current_time = local time
        self.current_time = from_time = datetime.now()

        if lifetime is None:
            lifetime = self.lifetime

        self.payload[claim] = datetime_to_epoch(from_time + lifetime)
