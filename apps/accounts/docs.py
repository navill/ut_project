from drf_yasg.openapi import *

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
                              'user': Schema(
                                  description='계정(User) 객체',
                                  type=TYPE_OBJECT,
                                  properties={
                                      'id': Schema(
                                          description='계정 pk',
                                          type=TYPE_INTEGER
                                      ),
                                      'email': Schema(
                                          description='계정 아이디로 사용될 이메일',
                                          type=TYPE_STRING,
                                          format=FORMAT_EMAIL
                                      ),
                                  }
                              ),
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
                "application/json":
                    {
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
                              'user': Schema(
                                  description='계정(User) 객체',
                                  type=TYPE_OBJECT,
                                  properties={
                                      'id': Schema(
                                          description='계정 pk',
                                          type=TYPE_INTEGER
                                      ),
                                      'email': Schema(
                                          description='계정 아이디로 사용될 이메일',
                                          type=TYPE_STRING,
                                          format=FORMAT_EMAIL
                                      ),
                                  }
                              ),
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
                "application/json":
                    {
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
