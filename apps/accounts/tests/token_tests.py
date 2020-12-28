import pytest

from accounts.api.authentications import CustomRefreshToken


@pytest.mark.django_db
def test_compare_user_token_expired_with_accesstoken_expired(user_doctor_with_group):
    user, doctor = user_doctor_with_group
    token = CustomRefreshToken.for_user(user)

    # 토큰 타입 검사
    assert token['token_type'] == 'refresh'
    assert token.access_token['token_type'] == 'access'

    # user 모델에 등록된 토큰 만료 시간과 발급된 토큰(access_token)의 만료 시간이 동일한지 확인
    assert token.access_token['exp'] == user.token_expired
