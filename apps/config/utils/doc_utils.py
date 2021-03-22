from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework import permissions


# drf-yasg에서 x-code extension을 사용하기 위한 custom schema(https://stackoverflow.com/a/61772496)
class CustomAutoSchema(SwaggerAutoSchema):
    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys=operation_keys)
        operation['x-code-samples'] = self.overrides.get('code_examples')
        operation['consumes'] = ["multipart/form-data"]
        return operation


schema_view = get_schema_view(
    openapi.Info(
        title="UT project API",
        default_version='v1',
        description="""
        ### [UTSOFT] 2-1과제 API 문서
        - 로그인, 회원가입 제외한 모든 서비스 접근은 반드시 헤더에 로그인 시 받은 access token을 전달해야 합니다.
        ### Content-type
        ```bash
            [POST, PUT, PATCH]: multipart/form-data
            [GET]: application/json
        ```
        ### Permission
            - IsOwner: 객체의 소유자(user)만 읽기 및 쓰기 가능
            - IsDoctor: 의사 계정만 읽기 및 쓰기 가능
            - IsPatient: 환자 계정만 읽기 및 쓰기 가능
            - CareDoctorReadOnly: 환자의 담당의사 계정만 해당 객체 읽기 가능
            - PatientReadOnly: 환자 계정만 읽기 가능
            - RelatedPatientReadOnly: 객체에 연결된(related) 환자 계정만 읽기 가능
            - WithRelated: 객체에 관계된 모든 계정이 읽기 및 쓰기 가능 
        
        """,
        # terms_of_service="https://www.google.com/policies/terms/",
        # contact=openapi.Contact(email="contact@snippets.local"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
