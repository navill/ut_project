from drf_yasg.openapi import *

medical_center_path_parameter = Parameter(
    name='id',
    description='병원 객체의 pk',
    in_=IN_PATH,
    type=TYPE_INTEGER
)

department_path_parameter = Parameter(
    name='id',
    description='부서 객체의 pk',
    in_=IN_PATH,
    type=TYPE_INTEGER
)

major_path_parameter = Parameter(
    name='id',
    description='전공 객체의 pk',
    in_=IN_PATH,
    type=TYPE_INTEGER
)

medical_center_schema = {
    'url': Schema(
        description='병원 세부 정보 url',
        type=TYPE_STRING
    ),
    'id': Schema(
        description='병원 객체의 pk',
        type=TYPE_INTEGER
    ),
    'country': Schema(
        description='병원이 위치한 나라',
        type=TYPE_STRING
    ),
    'city': Schema(
        description='병원이 위치한 도시',
        type=TYPE_STRING
    ),
    'name': Schema(
        description='병원 이름',
        type=TYPE_STRING
    ),
    'address': Schema(
        description='병원 상세 주소',
        type=TYPE_STRING
    ),
    'postal_code': Schema(
        description='병원 우편 번호',
        type=TYPE_STRING
    ),
    'main_call': Schema(
        description='병원 대표 번호',
        type=TYPE_STRING
    ),
    'sub_call': Schema(
        description='병원 보조 번호(고객 센터)',
        type=TYPE_STRING
    )
}
department_schema = {
    'url': Schema(
        description='부서 세부 정보 url',
        type=TYPE_STRING
    ),
    'id': Schema(
        description='부서 객체의 pk',
        type=TYPE_STRING
    ),
    'name': Schema(
        description='부서 이름',
        type=TYPE_STRING
    ),
    'call': Schema(
        description='부서 번호',
        type=TYPE_STRING
    ),
    'medical_center': Schema(
        description='병원 객체',
        type=TYPE_OBJECT
    ),
    'medical_center_id': Schema(
        description='병원 객체의 pk',
        type=TYPE_INTEGER
    )
}
major_schema = {
    'url': Schema(
        description='전공 세부 정보(detail) url',
        type=TYPE_STRING
    ),
    'id': Schema(
        description='전공 객체의 pk',
        type=TYPE_INTEGER,
    ),
    'name': Schema(
        description='전공 이름',
        type=TYPE_STRING
    ),
    'call': Schema(
        description='전공 전화 번호',
        type=TYPE_STRING
    ),
    'department': Schema(
        description='부서 객체',
        type=TYPE_OBJECT
    ),
    'department_id': Schema(
        description='부서 객체의 pk',
        type=TYPE_STRING
    )
}
medical_center_list = {
    "operation_summary": "[LIST] 병원 리스트",
    "operation_description":
        """
        - 기능: 등록된 병원 리스트 출력
        - 권한: AllowAny
        """,
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_ARRAY,
                description='병원 리스트',
                items=Schema(
                    type=TYPE_OBJECT,
                    properties={
                        **medical_center_schema
                    }
                ),
            ),
            description="병원 리스트 출력",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/medical-centers/1",
                        "id": 1,
                        "country": "대한민국",
                        "city": "서울특별시",
                        "name": "서울병원",
                        "address": "서울어딘가",
                        "postal_code": "123-123",
                        "main_call": "02-1111-1111",
                        "sub_call": "02-1111-1112"
                    }
                ]
            }
        )
    }
}
medical_center_detail = {
    'operation_summary': '[DETAIL] 병원 세부 정보',
    'operation_description':
        """
        - 기능: 등록된 병원의 세부 정보 출력
        - 권한: AllowAny
        """,
    'manual_parameters': [
        medical_center_path_parameter
    ],
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    **medical_center_schema
                }
            ),
            description="병원 리스트 출력",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/medical-centers/1",
                        "id": 1,
                        "country": "대한민국",
                        "city": "서울특별시",
                        "name": "서울병원",
                        "address": "서울어딘가",
                        "postal_code": "123-123",
                        "main_call": "02-1111-1111",
                        "sub_call": "02-1111-1112"
                    }
                ]
            }
        )
    }
}
medical_center_create = {
    "operation_summary": "[CREATE] 병원 등록",
    "operation_description":
        """
        - 기능: 병원 정보 등록
        - 권한: IsSuperUser
        """,
    'request_body': Schema(
        title='병원 객체 생성',
        type=TYPE_OBJECT,
        properties={
            'country': medical_center_schema['country'],
            'city': medical_center_schema['city'],
            'name': medical_center_schema['name'],
            'address': medical_center_schema['address'],
            'postal_code': medical_center_schema['postal_code'],
            'main_call': medical_center_schema['main_call'],
            'sub_call': medical_center_schema['sub_call']
        },
        required=['country', 'city', 'name', 'address', 'main_call']
    ),
    "responses": {
        "201": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    **medical_center_schema
                }
            ),
            description="병원 등록 결과",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/medical-centers/2",
                        "id": 2,
                        "country": "대한민국",
                        "city": "광주광역시",
                        "name": "유티병원",
                        "address": "동구 서석동",
                        "postal_code": "11-2223",
                        "main_call": "062-11111",
                        "sub_call": "062-22222"
                    }
                ]
            }
        )
    }
}
medical_center_update = {
    "operation_summary": "[UPDATE] 병원 정보 수정",
    "operation_description":
        """
        - 기능: 병원 정보 수정
        - 권한: IsSuperUser
        """,
    'manual_parameters': [
        medical_center_path_parameter
    ],
    'request_body': Schema(
        title='정보 수정',
        type=TYPE_OBJECT,
        properties={
            'country': medical_center_schema['country'],
            'city': medical_center_schema['city'],
            'address': medical_center_schema['address'],
            'postal_code': medical_center_schema['postal_code'],
            'main_call': medical_center_schema['main_call'],
            'sub_call': medical_center_schema['sub_call']
        },
    ),
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'name': medical_center_schema['name'],
                    'country': medical_center_schema['country'],
                    'city': medical_center_schema['city'],
                    'address': medical_center_schema['address'],
                    'postal_code': medical_center_schema['postal_code'],
                    'main_call': medical_center_schema['main_call'],
                    'sub_call': medical_center_schema['sub_call']
                }
            ),
            description="병원 등록 결과",
            examples={
                "application/json": [
                    {
                        "name": "유티병원",
                        "country": "대한민국",
                        "city": "광주광역시",
                        "address": "변경된 주소",
                        "postal_code": "11-2223",
                        "main_call": "062-11111",
                        "sub_call": "062-22222"
                    }
                ]
            }
        )
    }
}
medical_center_choice = {
    "operation_summary": "[LIST] 병원 선택 리스트",
    "operation_description":
        """
        - 기능: 병원에 대한 최소 정보(id, name) 리스트 및 필터링 기능
        - 권한: AllowAny
        ```python
        # example - query parameter
        http://127.0.0.1:8000/hospitals/choices/medical-centers?medical_center_name=서울병원&medical_center_id=1
        ```
        """,
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_ARRAY,
                description='병원 선택 리스트',
                items=Schema(
                    type=TYPE_OBJECT,
                    properties={
                        'id': medical_center_schema['id'],
                        'name': medical_center_schema['name']
                    }
                ),
            ),
            description="병원 선택 리스트",
            examples={
                "application/json": [
                    {
                        "id": 1,
                        "name": "서울병원"
                    },
                    {
                        "id": 2,
                        "name": "유티병원"
                    }
                ]
            }
        )
    }
}
department_list = {
    "operation_summary": "[LIST] 부서 리스트",
    "operation_description":
        """
        - 기능: 등록된 부서 리스트 출력
        - 권한: AllowAny
        """,
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_ARRAY,
                description='부서 리스트',
                items=Schema(
                    type=TYPE_OBJECT,
                    properties={
                        'url': department_schema['url'],
                        'id': department_schema['id'],
                        'name': department_schema['name'],
                        'call': department_schema['call'],
                    }
                ),
            ),
            description="부서 리스트 출력",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/departments/1",
                        "id": 1,
                        "name": "정신의학과",
                        "call": "02-1111-1112"
                    }
                ]
            }
        )
    }
}
department_detail = {
    'operation_summary': '[DETAIL] 부서 세부 정보',
    'operation_description':
        """
        - 기능: 등록된 부서의 세부 정보 출력
        - 권한: AllowAny
        """,
    'manual_parameters': [
        department_path_parameter
    ],
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': department_schema['url'],
                    'id': department_schema['id'],
                    'name': department_schema['name'],
                    'call': department_schema['call'],
                }
            ),
            description="부서 세부 정보 출력",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/departments/1",
                        "id": 1,
                        "name": "정신의학과",
                        "call": "02-1111-1112"
                    }
                ]
            }
        )
    }
}
department_create = {
    "operation_summary": "[CREATE] 부서 등록",
    "operation_description":
        """
        - 기능: 부서 정보 등록
        - 권한: IsSuperUser
        """,
    'request_body': Schema(
        title='부서 객체 생성',
        type=TYPE_OBJECT,
        properties={
            'name': department_schema['name'],
            'call': department_schema['call'],
            'medical_center': department_schema['medical_center_id']
        },
        required=['medical_center', 'name']
    ),
    "responses": {
        "201": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': department_schema['url'],
                    'id': department_schema['id'],
                    'name': department_schema['name'],
                    'call': department_schema['call'],
                    'medical_center': department_schema['medical_center_id']
                }
            ),
            description="부서 등록 결과",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/departments/2",
                        "id": 2,
                        "name": "흉부외과",
                        "call": "1111",
                        "medical_center": 1
                    }
                ]
            }
        )
    }
}
department_update = {
    "operation_summary": "[UPDATE] 부서 정보 수정",
    "operation_description":
        """
        - 기능: 부서 정보 수정
        - 권한: IsSuperUser
        """,
    'manual_parameters': [
        department_path_parameter
    ],
    'request_body': Schema(
        title='정보 수정',
        type=TYPE_OBJECT,
        properties={
            'name': department_schema['name'],
            'call': department_schema['call']
        },
    ),
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': department_schema['url'],
                    'id': department_schema['id'],
                    'name': department_schema['name'],
                    'call': department_schema['call']
                }
            ),
            description="부서 정보 수정 결과",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/departments/1",
                        "id": 1,
                        "name": "정신의학과",
                        "call": "0030"
                    }
                ]
            }
        )
    }
}

department_choice = {
    "operation_summary": "[LIST] 부서 선택 리스트",
    "operation_description":
        """
        - 기능: 부서에 대한 최소 정보(id, name) 리스트 및 필터링 기능
        - 권한: AllowAny
        ```python
        # example - query parameter
        http://127.0.0.1:8000/hospitals/choices/departments?medical_center_name=서울병원&medical_center_id=1&department_name=정신의학과&department_id=1        
        ```
        """,
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_ARRAY,
                description='부서 리스트',
                items=Schema(
                    type=TYPE_OBJECT,
                    properties={
                        'id': department_schema['id'],
                        'name': department_schema['name']
                    }
                ),
            ),
            description="부서 선택 리스트",
            examples={
                "application/json": [
                    {
                        "id": 1,
                        "name": "정신의학과"
                    },
                    {
                        "id": 2,
                        "name": "심리학과"
                    }
                ]
            }
        )
    }
}
major_list = {
    "operation_summary": "[LIST] 전공 리스트",
    "operation_description":
        """
        - 기능: 등록된 전공 리스트 출력
        - 권한: AllowAny
        """,
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_ARRAY,
                description='전공 리스트',
                items=Schema(
                    type=TYPE_OBJECT,
                    properties={
                        'url': major_schema['url'],
                        'id': major_schema['id'],
                        'name': major_schema['name'],
                        'call': major_schema['call'],
                    }
                ),
            ),
            description="전공 리스트 출력",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/majors/1",
                        "id": 1,
                        "name": "정신의학",
                        "call": "02-1111-1113"
                    },
                    {
                        "url": "http://127.0.0.1:8000/hospitals/majors/2",
                        "id": 2,
                        "name": "흉부외과",
                        "call": "02-1123-1223"
                    }
                ]
            }
        )
    }
}
major_detail = {
    'operation_summary': '[DETAIL] 전공 세부 정보',
    'operation_description':
        """
        - 기능: 등록된 전공의 세부 정보 출력
        - 권한: AllowAny
        """,
    'manual_parameters': [
        major_path_parameter
    ],
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': major_schema['url'],
                    'id': major_schema['id'],
                    'name': major_schema['name'],
                    'call': major_schema['call'],
                }
            ),
            description="전공 세부 정보 출력",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/majors/1",
                        "id": 1,
                        "name": "정신의학",
                        "call": "02-1111-1113"
                    },
                    {
                        "url": "http://127.0.0.1:8000/hospitals/majors/2",
                        "id": 2,
                        "name": "흉부외과",
                        "call": "02-1123-1223"
                    }
                ]
            }
        )
    }
}
major_create = {
    "operation_summary": "[CREATE] 전공 등록",
    "operation_description":
        """
        - 기능: 전공 정보 등록
        - 권한: IsSuperUser
        """,
    'request_body': Schema(
        title='전공 객체 생성',
        type=TYPE_OBJECT,
        properties={
            'name': major_schema['name'],
            'call': major_schema['call'],
            'department': major_schema['department_id']
        },
        required=['medical_center', 'name']
    ),
    "responses": {
        "201": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': major_schema['url'],
                    'id': major_schema['id'],
                    'name': major_schema['name'],
                    'call': major_schema['call'],
                    'department': major_schema['department']
                }
            ),
            description="전공 등록 결과",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/majors/3",
                        "id": 3,
                        "name": "흉부의학",
                        "call": "0000",
                        "department": 2
                    }
                ]
            }
        )
    }
}
major_update = {
    "operation_summary": "[UPDATE] 전공 정보 수정",
    "operation_description":
        """
        - 기능: 전공 정보 수정
        - 권한: IsSuperUser
        """,
    'manual_parameters': [
        major_path_parameter
    ],
    'request_body': Schema(
        title='정보 수정',
        type=TYPE_OBJECT,
        properties={
            'name': major_schema['name'],
            'call': major_schema['call']
        },
    ),
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': major_schema['url'],
                    'id': major_schema['id'],
                    'name': major_schema['name'],
                    'call': major_schema['call']
                }
            ),
            description="전공 정보 수정 결과",
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/hospitals/departments/1",
                        "id": 1,
                        "name": "정신의학과",
                        "call": "1111"
                    }
                ]
            }
        )
    }
}
major_choice = {
    "operation_summary": "[LIST] 전공 선택 리스트",
    "operation_description":
        """
        - 기능: 전공에 대한 최소 정보(id, name) 리스트 및 필터링 기능
        - 권한: AllowAny
        ```python
        # example - query parameter
        http://127.0.0.1:8000/hospitals/choices/majors?department_name=정신의학과&department_id=1&major_name=정신의학&major_id=1        
        ```
        """,
    "responses": {
        "200": Response(
            schema=Schema(
                type=TYPE_ARRAY,
                description='전공 리스트',
                items=Schema(
                    type=TYPE_OBJECT,
                    properties={
                        'id': department_schema['id'],
                        'name': department_schema['name']
                    }
                ),
            ),
            description="전공 선택 리스트",
            examples={
                "application/json": [
                    {
                        "id": 1,
                        "name": "정신의학"
                    },
                    {
                        "id": 2,
                        "name": "흉부의학"
                    }
                ]
            }
        )
    }
}
