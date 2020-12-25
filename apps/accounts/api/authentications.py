from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token, BlacklistMixin, AccessToken

User = get_user_model()


class CustomJWTTokenUserAuthentication(JWTAuthentication):
    def authenticate(self, request):

        if super().authenticate(request) is None:
            # authentication 실패 시 None 반환되기 때문에 이 구문이 없을 경우
            # TypeError: cannot unpack...
            return None

        user, validated_token = super().authenticate(request)
        if user.token_expired != validated_token.payload['exp']:
            raise AuthenticationFailed('User do not have valid token', code='user_without_token')

        return user, validated_token

    def get_user(self, validated_token):
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


class CustomToken(Token):
    token_type = None
    lifetime = None

    def __init__(self, token=None, verify=True):
        super().__init__(token, verify)
        self.current_time = timezone.now()  # local time 적용
        self.token = token

        if token is None:
            """
            Token.__init__() 시 set_exp가 실행되면서 CutstomToken.current_time이
            적용되지 않기 때문에 아래에서 강제로 실행(아래와 같이 할 경우 같은 메서드(set_exp)가 두번 실행되어야 하는 문제가 있음)
            """
            self.set_exp(from_time=self.current_time)
            self.set_jti()


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
    def for_user(cls, user) -> Token:
        token = super().for_user(user)
        expired_time = int(token.access_token.payload['exp'])
        user.set_token_expired(expired_time)  # login 시 user.token_expired 갱신
        return token

    @property
    def access_token(self):
        access = AccessToken()
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access
