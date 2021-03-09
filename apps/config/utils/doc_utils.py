from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework import permissions


# drf-yasg에서 x-code extension을 사용하기 위한 custom schema(https://stackoverflow.com/a/61772496)
class CustomAutoSchema(SwaggerAutoSchema):
    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys=operation_keys)
        operation['x-code-samples'] = self.overrides.get('code_examples')
        operation['consumes'] = ["multipart/form-data", "application/x-www-form-urlencoded"]
        return operation


schema_view = get_schema_view(
    openapi.Info(
        title="UT project API",
        default_version='v1',
        description="""
        ### [UTSOFT] 2-1과제 API 문서
        - 로그인, 회원가입 제외한 모든 서비스 접근은 반드시 헤더에 로그인 시 받은 access token을 전달해야 합니다.
        - POST, PUT, PATCH 메서드의 Content-Type은 "multipart/form-data"으로 전달해야합니다.
        - GET 메서드는 "application/json" 타입으로 반환합니다.  
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
