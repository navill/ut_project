from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.openapi import Parameter
from drf_yasg.views import get_schema_view
from drf_yasg.inspectors import SwaggerAutoSchema, CoreAPICompatInspector, NotHandled
from rest_framework import permissions


class CustomAutoSchema(SwaggerAutoSchema):
    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys=operation_keys)
        operation['x-code-samples'] = self.overrides.get('code_examples')
        operation['consumes'] = ["multipart/form-data"]
        return operation

    def get_pagination_parameters(self):
        result = super().get_pagination_parameters()

        for param in result:
            if param.name == 'limit':
                param.description = '한 페이지에 출력할 요소의 수'
            elif param.name == 'offset':
                param.description = '화면에 출력될 요소의 오프셋(시작점)'

        return result


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_security_definitions(self):
        security_definition = {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description':
                    """
                    ### 서비스 접근
                    ```bash            
                    curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiL..." -X GET http://localhost:8000/...
                    ```
                    - service access: 회원가입과 로그인을 제외한 모든 서비스 접근 시 헤더에 access token 값을 포함해야함.

                    ```bash
                    curl -X POST -d"email=test@test.com&password=test1234" http://localhost:8000/token
                    ```
                    - login -> refresh, access token 반환(status_code=201) 

                    ```bash
                    curl -H "Authorization: Bearer eyJ0eXAiOi...WbyjSVk" -X POST -d"refresh=eyJ0eXAiOiJK...0OSdp0" http://localhost:8000/token/logout 
                    ```
                    - logout -> None 반환(status_code=205)
                    """
            },
        }
        return security_definition


class CommonFilterDescriptionInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            result = super().get_filter_parameters(filter_backend)
            for param in result:
                if not param.get('description', ''):
                    param.description = "{field_name} 파라미터".format(field_name=param.name)

            return result

        return NotHandled


schema_view = get_schema_view(
    openapi.Info(
        title="UT project API",
        default_version='v1',
        description="""
        ### [UTSOFT] 2-1과제 API 문서
        - 로그인, 회원가입 제외한 모든 서비스 접근은 반드시 헤더에 로그인 시 받은 access token을 전달해야 합니다. \n
        ### Content-type
        ```bash
        [POST, PUT]: multipart/form-data
        [GET]: application/json
        ```
        ### Permission
        - IsOwner: 객체의 소유자(user)만 읽기 및 쓰기 가능
        - IsDoctor: 의사 계정만 읽기 및 쓰기 가능
        - IsPatient: 환자 계정만 읽기 및 쓰기 가능
        - CareDoctorReadOnly: 환자의 담당의사 계정만 해당 객체 읽기 가능
        - PatientReadOnly: 환자 계정만 읽기 가능
        - RelatedPatientReadOnly: 객체에 연결된(related) 환자 계정만 읽기 가능
        - WithRelated: 객체에 관계된 모든 계정이 읽기 및 쓰기 가능 \n
        
        ### Pagination(전체 API(LIST)에 적용)\n
        - page limit(default: 30): 몇 개의 요소를 출력 할 것인지 
        - page offset: 몇 번째 요소부터 출력 할 것인지
            - 한 페이지에 첫 번째 요소(offset=0)부터 30개의 요소(limit)를 출력(1.page - 1~30)
            ```http://127.0.0.1:8000/prescriptions/choices/file-prescriptions?limit=30```
            - 한 페이지에 31번째 요소(offset=30)부터 30개의 요소(limit)를 출력(2.page - 31~60)
            ```http://127.0.0.1:8000/prescriptions/choices/file-prescriptions?limit=30&offset=30```\n
        **기본적으로 api 호출 시 앞, 뒤 페이지에 대한 url을 출력**
        - next: 현재 페이지를 기준으로 다음 페이지의 url
        - previous: 현재 페이지를 기준으로 이전 페이지의 url\n
        
        **예시** \n
        [3번 페이지] \n
        ```"next": "http://127.0.0.1:8000/prescriptions/choices/file-prescriptions?limit=30&offset=60"``` \n
        [1번 페이지] \n
        ```"previous": "http://127.0.0.1:8000/prescriptions/choices/file-prescriptions?limit=30"```  
        """,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator
)


def converted_parameters_from(schemas):
    result = {}
    for name, schema in schemas.items():
        description = schema.description
        type_ = schema.type
        format_ = schema.format if hasattr(schema, 'format') else None
        result[name] = Parameter(name=name, description=description, type=type_, format=format_, in_=openapi.IN_QUERY)
    return result
