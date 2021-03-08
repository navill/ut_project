from drf_yasg.openapi import *

doctor_url_schema = {
    'url': Schema(
        description='doctor detail url',
        type=TYPE_STRING,
        format=FORMAT_URI
    )
}
patient_url_schema = {
    'url': Schema(
        description='patient detail url',
        type=TYPE_STRING,
        format=FORMAT_URI
    )
}
user_schema = {
    'user': Schema(
        description='계정(User) 객체',
        type=TYPE_OBJECT,
        properties={
            'email': Schema(
                description='계정 아이디로 사용될 이메일',
                type=TYPE_STRING,
                format=FORMAT_EMAIL
            ),
            'password': Schema(
                description='계정 비밀번호',
                type=TYPE_STRING,
                format=FORMAT_PASSWORD
            ),
            'password2': Schema(
                description='계정 비밀번호 확인',
                type=TYPE_STRING,
                format=FORMAT_PASSWORD
            )
        }
    ),
}
account_schema = {
    'first_name': Schema(
        description='사용자의 이름',
        type=TYPE_STRING
    ),
    'last_name': Schema(
        description='사용자의 성',
        type=TYPE_STRING
    ),
    'gender': Schema(
        description='성별',
        enum=['MALE', 'FEMALE'],
        type=TYPE_STRING
    ),
    'address': Schema(
        description='주소',
        type=TYPE_STRING
    ),
    'phone': Schema(
        description='연락처',
        type=TYPE_STRING
    ),
}

doctor_signup = {
    'operation_summary': '[CREATE] 의사 계정 생성',
    'operation_description': """
    - 기능: 의사 계정 생성
    - 권한: AllowAny
    """,
    'request_body': Schema(
        title='계정 생성',
        type=TYPE_OBJECT,
        properties={
            **user_schema,
            **account_schema,
            'description': Schema(
                description='의사 소개',
                type=TYPE_STRING
            ),
            'major': Schema(
                description='전공(객체) pk',
                type=TYPE_INTEGER
            )
        },
        required=['user', 'first_name', 'last_name', 'gender', 'address', 'phone', 'major']
    ),
    'responses': {
        '201': Response(
            schema=Schema(type=TYPE_OBJECT,
                          properties={
                              **user_schema,

                              'description': Schema(
                                  description='의사 소개',
                                  type=TYPE_STRING
                              ),
                              'major': Schema(
                                  description='전공(객체) pk',
                                  type=TYPE_INTEGER
                              )
                          }, ),
            description='소견서 작성 완료',
            examples={
                "application/json": {
                    "url": "http://127.0.0.1:8000/accounts/doctors/11",
                    "gender": "MALE",
                    "user": {
                        "id": 11,
                        "email": "doctor_test00@test.com"
                    },
                    "first_name": "광주",
                    "last_name": "의사",
                    "address": "광주광역시",
                    "phone": "010-111-1111",
                    "description": "",
                    "major": 1
                }
            }
        ),
    }
}
doctor_list = {
    'operation_summary': '[LIST] 의사 리스트',
    'operation_description': """
    - 기능: 등록된 의사 리스트 출력
    - 권한: Admin
    """,
    'responses': {
        '201': Response(
            schema=Schema(type=TYPE_OBJECT,
                          properties={
                              'url': Schema(
                                  description='detail url',
                                  type=TYPE_STRING,
                                  format=FORMAT_URI
                              ),
                              'user': Schema(
                                  description='User 객체 pk',
                                  type=TYPE_INTEGER
                              ),
                              'major': Schema(
                                  description='의사 전공 이름',
                                  type=TYPE_STRING
                              ),
                              'first_name': account_schema['first_name'],
                              'last_name': account_schema['last_name'],
                              'gender': account_schema['gender'],
                              'created_at': Schema(
                                  description='계정 생성일',
                                  type=TYPE_STRING,
                                  format=FORMAT_DATETIME
                              )
                          },
                          ),
            description='의사 리스트',
            examples={
                "application/json":
                    [
                        {
                            "detail_url": "http://127.0.0.1:8000/accounts/doctors/11",
                            "user": 11,
                            "major": "정신의학",
                            "first_name": "광주",
                            "last_name": "의사",
                            "gender": "남",
                            "created_at": "2021-03-08T16:08:31.187556"
                        },
                        {
                            "detail_url": "http://127.0.0.1:8000/accounts/doctors/4",
                            "user": 4,
                            "major": "정신의학",
                            "first_name": "의사",
                            "last_name": "삼",
                            "gender": "남",
                            "created_at": "2021-01-27T13:10:28.794673"
                        }
                    ]
            }
        ),
    }}
doctor_detail = {
    'operation_summary': '[DETAIL] 의사 세부 정보',
    'operation_description': """
    - 기능: 등록된 의사의 세부 정보 출력
    - 권한: IsOwner or RelatedPatientReadOnly
    """,
    'manual_parameters': [
        Parameter(
            name='user',
            description='의사 객체의 pk',
            in_=IN_PATH,
            type=TYPE_INTEGER
        )
    ],
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': Schema(
                        description='update url',
                        type=TYPE_STRING,
                        format=FORMAT_URI
                    ),
                    'user': Schema(
                        description='의사 객체 pk',
                        type=TYPE_INTEGER
                    ),
                    'major': Schema(
                        description='의사 전공 이름',
                        type=TYPE_STRING
                    ),
                    **account_schema,
                    'created_at': Schema(
                        description='계정 생성일',
                        type=TYPE_STRING,
                        format=FORMAT_DATETIME
                    ),
                    'description': Schema(
                        description='의사 간략 소개',
                        type=TYPE_STRING
                    )
                }
            ),
            description='의사 정보 출력',
            examples={
                "url": "http://127.0.0.1:8000/accounts/doctors/2/update",
                "user": 2,
                "major": "정신의학",
                "first_name": "의사",
                "last_name": "일",
                "gender": "남",
                "created_at": "2021-01-27T13:09:58.512592",
                "address": "서울특별시",
                "phone": "111",
                "description": "첫 번째 의사"
            }
        )
    }
}

doctor_update = {
    'operation_summary': '[UPDATE] 의사 세부 정보 수정',
    'operation_description': """
    - 기능: 등록된 의사의 세부 정보 수정
    - 권한: IsOwner
    """,
    'manual_parameters': [
        Parameter(
            name='user',
            description='의사 객체의 pk',
            in_=IN_PATH,
            type=TYPE_INTEGER
        )
    ],
    'request_body': Schema(
        title='계정 정보 수정',
        type=TYPE_OBJECT,
        properties={
            'address': account_schema['address'],
            'phone': account_schema['phone'],
            'description': Schema(
                description='의사 소개',
                type=TYPE_STRING
            ),
        },
    ),
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'address': account_schema['address'],
                    'phone': account_schema['phone'],
                    'description': Schema(
                        description='의사 간략 소개',
                        type=TYPE_STRING
                    )

                }
            ),
            description='의사 정보 출력',
            examples={
                'application/json': {
                    "address": "광주",
                    "phone": "010-11-1234",
                    "description": "내용이 수정되었습니다."
                }
            }
        )
    }

}

patient_signup = {
    'operation_summary': '[CREATE] 환자 계정 생성',
    'operation_description': """
    - 기능: 환자 계정 생성
    - 권한: AllowAny
    """,
    'request_body': Schema(
        title='계정 생성',
        type=TYPE_OBJECT,
        properties={
            **user_schema,
            **account_schema,
            'birth': Schema(
                description='환자의 생년월일',
                type=TYPE_STRING,
                format=FORMAT_DATE
            ),
            'emergency_call': Schema(
                description='응급 전화번호',
                type=TYPE_STRING
            ),
            'doctor': Schema(
                description='담당 의사 객체의 pk',
                type=TYPE_INTEGER
            )
        },
        required=['user', 'first_name', 'last_name', 'gender', 'address', 'phone', 'major']
    ),
    'responses': {
        '201': Response(
            schema=Schema(type=TYPE_OBJECT,
                          properties={
                              'url': Schema(
                                  description='detail url',
                                  type=TYPE_STRING,
                                  format=FORMAT_URI
                              ),
                              **user_schema,
                              **account_schema,
                              'birth': Schema(
                                  description='환자의 생년월일',
                                  type=TYPE_STRING,
                                  format=FORMAT_DATE
                              ),
                              'emergency_call': Schema(
                                  description='응급 전화번호',
                                  type=TYPE_STRING
                              ),
                              'doctor': Schema(
                                  description='담당 의사 객체의 pk',
                                  type=TYPE_INTEGER
                              )
                          }, ),
            description='환자 계정 생성',
            examples={
                "application/json": {
                    "detail_url": "http://127.0.0.1:8000/accounts/patients/15",
                    "user": {
                        "id": 15,
                        "email": "patientzz@patientzz.com"
                    },
                    "first_name": "환자",
                    "last_name": "김",
                    "gender": "MALE",
                    "birth": "1988-03-03",
                    "address": "광주광역시",
                    "phone": "010-1121-1111",
                    "emergency_call": "010-10023",
                    "doctor": 2
                }
            }
        ),

    }
}

patient_list = {
    'operation_summary': '[LIST] 환자 계정 리스트',
    'operation_description': """
    - 기능: 로그인한 의사의 계정에 연결된 환자의 리스트 출력
    - 권한: IsDoctor
    """,
    'responses': {
        '200': Response(
            schema=Schema(type=TYPE_OBJECT,
                          properties={
                              'url': Schema(
                                  description='detail url',
                                  type=TYPE_STRING,
                                  format=FORMAT_URI
                              ),
                              'doctor': Schema(
                                  description='담당 의사 객체의 pk',
                                  type=TYPE_INTEGER
                              ),
                              'age': Schema(
                                  description='환자의 만 나이',
                                  type=TYPE_INTEGER
                              ),
                              'first_name': account_schema['first_name'],
                              'last_name': account_schema['last_name'],
                              'gender': account_schema['gender'],
                              'created_at': Schema(
                                  description='계정 생성일',
                                  type=TYPE_STRING,
                                  format=FORMAT_DATETIME
                              )

                          }, ),
            description='의사 계정에 연결된 환자의 리스트 출력',
            examples={
                "application/json": [
                    {
                        "url": "http://127.0.0.1:8000/accounts/patients/15",
                        "user": 15,
                        "doctor": 2,
                        "age": 33,
                        "first_name": "환자",
                        "last_name": "김",
                        "gender": "남",
                        "created_at": "2021-03-08T18:26:44.667994"
                    },
                    {
                        "url": "http://127.0.0.1:8000/accounts/patients/13",
                        "user": 13,
                        "doctor": 2,
                        "age": 33,
                        "first_name": "환자",
                        "last_name": "김",
                        "gender": "남",
                        "created_at": "2021-03-08T18:26:01.873935"
                    },
                ]
            }
        ),

    }
}

patient_detail = {
    'operation_summary': '[DETAIL] 환자 세부 정보',
    'operation_description': """
    - 기능: 환자의 세부 정보 출력
    - 권한: CareDoctorReadOnly or IsOwner
    """,
    'manual_parameters': [
        Parameter(
            name='user',
            description='환자 객체의 pk',
            in_=IN_PATH,
            type=TYPE_INTEGER
        )
    ],
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': Schema(
                        description='update url',
                        type=TYPE_STRING,
                        format=FORMAT_URI
                    ),
                    'user': Schema(
                        description='환자 객체 pk',
                        type=TYPE_INTEGER
                    ),
                    'doctor': Schema(
                        description='의사 객체 pk',
                        type=TYPE_INTEGER
                    ),
                    'age': Schema(
                        description='환자의 만 나이',
                        type=TYPE_INTEGER
                    ),
                    **account_schema,
                    'created_at': Schema(
                        description='계정 생성일',
                        type=TYPE_STRING,
                        format=FORMAT_DATETIME
                    ),
                    'emergency_call': Schema(
                        description='보호자 또는 응급 전화 번호',
                        type=TYPE_STRING
                    )

                }
            ),
            description='환자 정보 출력',
            examples={
                'application/json': {
                    "url": "http://127.0.0.1:8000/accounts/patients/15/update",
                    "user": 15,
                    "doctor": 2,
                    "age": 33,
                    "first_name": "환자",
                    "last_name": "김",
                    "gender": "남",
                    "address": "광주광역시",
                    "phone": "010-1121-1111",
                    "created_at": "2021-03-08T18:26:44.667994",
                    "emergency_call": "010-10023"
                }
            }
        )
    }

}

patient_update = {
    'operation_summary': '[UPDATE] 환자 세부 정보 수정',
    'operation_description': """
    - 기능: 환자의 세부 정보 수정
    - 권한: IsOwner
    """,
    'manual_parameters': [
        Parameter(
            name='user',
            description='환자 객체의 pk',
            in_=IN_PATH,
            type=TYPE_INTEGER
        )
    ],
    'request_body': Schema(
        title='계정 정보 수정',
        type=TYPE_OBJECT,
        properties={
            'address': account_schema['address'],
            'phone': account_schema['phone'],
            'emergency_call': Schema(
                description='보호자 또는 응급 전화 번호',
                type=TYPE_STRING
            ),
        },
    ),
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'address': account_schema['address'],
                    'phone': account_schema['phone'],
                    'emergency_call': Schema(
                        description='보호자 또는 응급 전화 번호',
                        type=TYPE_STRING
                    ),
                }
            ),
            description='환자 정보 출력',
            examples={
                "application/json": {
                    "address": "수정된 광주광역시",
                    "phone": "010-1212-1212",
                    "emergency_call": "010-2121-2121"
                }
            }
        )
    }

}
