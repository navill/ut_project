from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


# [Deprecated]
# def staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
#     decorator = user_passes_test(
#         # user = request.user
#         lambda user: user.is_active and user.is_doctor,
#         login_url=login_url,
#         redirect_field_name=redirect_field_name
#     )
#     if function:
#         return decorator(function)
#     return decorator
#
#
# def normal_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
#     decorator = user_passes_test(
#         lambda user: not user.is_doctor and user.is_patient,
#         login_url=login_url,
#         redirect_field_name=redirect_field_name
#     )
#     if function:
#         return decorator(function)
#     return decorator
