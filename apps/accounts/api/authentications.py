from typing import Dict, AnyStr, Tuple, Union, NoReturn

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.authentication import BasicAuthentication
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token, BlacklistMixin, AccessToken

User = get_user_model()


def set_type_for(user: User) -> NoReturn:
    group_name = list(user.groups.values_list('name', flat=True))[0]
    user.set_user_type(group_name)


class CustomJWTTokenUserAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> Union[Tuple[User, Dict[str, AnyStr]], None]:
        try:
            user, validated_token = super().authenticate(request)
        except TypeError:
            return None

        if user.token_expired != validated_token.payload['exp']:
            raise AuthenticationFailed("User don't have valid token", code='invalid_token')
        return user, validated_token

    def get_user(self, validated_token: Dict[str, AnyStr]) -> User:
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = User.objects.only(api_settings.USER_ID_FIELD).get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        set_type_for(user)
        return user


class CustomBaseAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        user, _ = super().authenticate_credentials(userid, password, request=request)
        set_type_for(user)
        return user, _


class CustomToken(Token):
    token_type = None
    lifetime = None

    def __init__(self, token: AnyStr = None, verify: bool = True):
        super().__init__(token, verify)
        self.current_time = timezone.now()  # local time 적용
        self.token = token


class CustomRefreshToken(BlacklistMixin, CustomToken):
    token_type = 'refresh'
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        'exp',
        api_settings.JTI_CLAIM,
        'jti',
    )

    @classmethod
    @transaction.atomic
    def for_user(cls, user: User, raise_error: bool = False) -> 'CustomRefreshToken':
        token = super().for_user(user)
        access_token_exp = int(token.access_token.payload['exp'])

        if raise_error:
            raise Exception('for test')

        user.set_token_expired(access_token_exp)
        return token

    @property
    def access_token(self) -> AccessToken:
        access = AccessToken()
        access.set_exp(from_time=self.current_time)
        no_copy = self.no_copy_claims

        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access
