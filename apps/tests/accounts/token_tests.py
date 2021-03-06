import time

import pytest
from rest_framework.reverse import reverse
from rest_framework_simplejwt.token_blacklist.models import *
from rest_framework_simplejwt.utils import datetime_from_epoch

from accounts.api.authentications import CustomJWTTokenUserAuthentication, CustomRefreshToken
from accounts.models import *


@pytest.mark.django_db
def test_custom_refresh_token():
    user = BaseUser.objects.get(id=2)

    # expired time
    token = CustomRefreshToken.for_user(user)
    assert user.token_expired == token.access_token['exp']
    assert BlacklistedToken.objects.all().exists() is False

    outstanding_token = OutstandingToken.objects.first()
    assert outstanding_token.token == str(token)
    assert outstanding_token.jti == token['jti']
    assert outstanding_token.expires_at == datetime_from_epoch(token['exp'])

    token.blacklist()
    black_token = BlacklistedToken.objects.get(token_id=outstanding_token.id)
    assert black_token


@pytest.mark.django_db
def test_token_for_user_with_error(doctor_with_group):
    with pytest.raises(Exception):
        CustomRefreshToken.for_user(doctor_with_group.user, raise_error=True)

    # CustomRefreshToken.for_user() 중간에 에러가 발생할 경우 user.token_expired=<epoch_time> 및 OutstandingToken은 생성되면 안됨
    assert doctor_with_group.user.token_expired == 0
    assert OutstandingToken.objects.all().exists() is False

    CustomRefreshToken.for_user(doctor_with_group.user)
    assert doctor_with_group.user.token_expired != 0


@pytest.mark.django_db
def test_authenticate_jwt_token_user(rf):
    doctor = Doctor.objects.first()
    token = CustomRefreshToken.for_user(doctor.user)
    access_token = token.access_token

    url = reverse('token-login')
    request = rf.post(url, HTTP_AUTHORIZATION=f'Bearer {str(access_token)}')
    authentication = CustomJWTTokenUserAuthentication()
    auth_user, validated_token = authentication.authenticate(request)

    assert auth_user == doctor.user
    assert token['token_type'] == 'refresh'
    assert access_token['token_type'] == 'access'
    assert access_token['jti'] == validated_token['jti']


@pytest.mark.django_db
def test_compare_user_token_expired_with_accesstoken_expired(get_token_from_doctor):
    doctor = Doctor.objects.first()
    token = CustomRefreshToken.for_user(doctor.user)
    access_token = token.access_token
    # 토큰 타입 검사
    assert get_token_from_doctor['token_type'] == 'refresh'
    assert access_token['token_type'] == 'access'
    # user 모델에 등록된 토큰 만료 시간과 발급된 토큰(access_token)의 만료 시간이 동일한지 확인
    assert access_token['exp'] == doctor.user.token_expired
