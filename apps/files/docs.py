from drf_yasg.openapi import *

common_file_schema = {
    'url': Schema(
        description='detail url',
        type=TYPE_STRING,
        format=FORMAT_URI
    ),
    'download_url': Schema(
        description='download url',
        type=TYPE_STRING,
        format=FORMAT_URI
    ),
    'update_url': Schema(
        description='update url',
        type=TYPE_STRING,
        format=FORMAT_URI
    ),
    'id': Schema(
        description="파일 객체의 id",
        type=TYPE_STRING,
        format=FORMAT_UUID
    ),
    'created_at': Schema(
        description='파일 생성(업로드)일',
        type=TYPE_STRING,
        format=FORMAT_DATETIME
    ),
    'deleted': Schema(
        description='삭제된 파일인지 여부',
        type=TYPE_BOOLEAN
    ),
    'uploader_name': Schema(
        description='업로더의 이름(full name)',
        type=TYPE_STRING
    ),
}
doctor_file_schema = {
    'prescription': Schema(
        description='소견서의 pk',
        type=TYPE_INTEGER
    ),
    'file': Schema(
        description='의사가 업로드한 파일(파일 경로)',
        type=TYPE_FILE
    ),
    'uploader': Schema(
        description='업로더(의사 계정)의 pk',
        type=TYPE_INTEGER
    ),
}
patient_file_schema = {
    'file_prescription': Schema(
        description='환자 파일과 연결된 스케줄(FilePrescription) 객체의 pk',
        type=TYPE_INTEGER
    ),
    'uploader': Schema(
        description='업로더(환자 계정)의 pk',
        type=TYPE_INTEGER
    ),
    'file': Schema(
        description='환자가 업로드한 파일(파일 경로)',
        type=TYPE_FILE
    ),
}

doctor_file_list = {
    'operation_summary': '[LIST] 의사가 올린 파일 리스트',
    'operation_description': """
    - 기능: 로그인한 의사 계정으로 올린 파일의 리스트를 출력
    - 권한: IsDoctor
    """,
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_ARRAY,
                items=Schema(
                    type=TYPE_OBJECT,
                    properties={
                        'url': common_file_schema['url'],
                        'download_url': common_file_schema['download_url'],
                        'id': common_file_schema['id'],
                        'prescription': doctor_file_schema['prescription'],
                        'file': doctor_file_schema['file'],
                        'uploader': doctor_file_schema['uploader'],
                        'created_at': common_file_schema['created_at'],
                        'uploader_name': common_file_schema['uploader_name']
                    }
                )
            ),
            description='파일 리스트 출력',
            examples={
                'application/json': [
                    {
                        "url": "http://127.0.0.1:8000/datafiles/doctor-files/638b8c4f-a27e-4f19-86ba-a443c54cb907",
                        "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/638b8c4f-a27e-4f19-86ba-a443c54cb907/download",
                        "id": "638b8c4f-a27e-4f19-86ba-a443c54cb907",
                        "prescription": 23,
                        "file": "2021-03-06/md/doctor1doctor.com_221020_test_oTkswZ2.md",
                        "uploader": 2,
                        "created_at": "2021-03-06T22:10:20.836960",
                        "uploader_name": "의사일"
                    },
                    {
                        "url": "http://127.0.0.1:8000/datafiles/doctor-files/c16f7176-8ebd-4222-992a-75ccda9f8778",
                        "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/c16f7176-8ebd-4222-992a-75ccda9f8778/download",
                        "id": "c16f7176-8ebd-4222-992a-75ccda9f8778",
                        "prescription": 23,
                        "file": "2021-03-06/md/doctor1doctor.com_221020_test.md",
                        "uploader": 2,
                        "created_at": "2021-03-06T22:10:20.734439",
                        "uploader_name": "의사일"
                    },
                ]
            }
        )
    }
}

doctor_file_create = {
    "operation_summary": "[CREATE] 의사 파일 업로드",
    "operation_description": """
    - 기능: 의사가 소견서에 파일 업로드
    - 권한: IsDoctor
    """,
    "request_body": Schema(
        title="파일 업로드",
        type=TYPE_OBJECT,
        properties={
            'prescription': doctor_file_schema['prescription'],
            'file': doctor_file_schema['file']
        },
        required=['prescription', 'file']
    ),
    "responses": {
        "201": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': common_file_schema['url'],
                    'download_url': common_file_schema['download_url'],
                    'id': common_file_schema['id'],
                    'prescription': doctor_file_schema['prescription'],
                    'created_at': common_file_schema['created_at']
                }
            ),
            description="파일 업로드 결과",
            examples={
                'application/json': {
                    "url": "http://127.0.0.1:8000/datafiles/doctor-files/444a2710-f10a-4893-b7a8-5a7d6f336dbb",
                    "id": "444a2710-f10a-4893-b7a8-5a7d6f336dbb",
                    "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/444a2710-f10a-4893-b7a8-5a7d6f336dbb/download",
                    "prescription": 22,
                    "created_at": "2021-03-09T17:30:51.641123"
                }
            }
        )
    }
}

doctor_file_detail = {
    "operation_summary": "[DETAIL] 의사 파일 세부 정보",
    "operation_description": """
    - 기능: 의사가 업로드한 파일의 세부 정보 출력(detail page)
    - 권한: IsOwner
    """,
    'manual_parameters': [
        Parameter(
            name='id',
            description='파일 객체의 pk(uuid)',
            in_=IN_PATH,
            type=TYPE_STRING,
            format=FORMAT_UUID
        )
    ],
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'update_url': common_file_schema['update_url'],
                    'download_url': common_file_schema['download_url'],
                    'id': common_file_schema['id'],
                    'prescription': doctor_file_schema['prescription'],
                    'file': doctor_file_schema['file'],
                    'uploader': doctor_file_schema['uploader'],
                    'created_at': common_file_schema['created_at'],
                    'deleted': common_file_schema['deleted']
                }
            ),
            description="의사가 올린 파일의 세부정보 출력",
            examples={
                'application/json': {
                    "update_url": "http://127.0.0.1:8000/datafiles/doctor-files/444a2710-f10a-4893-b7a8-5a7d6f336dbb/update",
                    "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/acefb67f-e41a-4a9d-82ce-0dec0a0b4fbb/download",
                    "id": "acefb67f-e41a-4a9d-82ce-0dec0a0b4fbb",
                    "prescription": 22,
                    "file": "2021-03-09/md/doctor1doctor.com_171001_test.md",
                    "uploader": 2,
                    "created_at": "2021-03-09T17:10:01.141603",
                    "deleted": "false"
                }
            }
        )
    }
}

doctor_file_update = {
    'operation_summary': '[UPDATE] 의사 파일 정보 수정',
    'operation_description': """
    - 기능: 업로드된 파일 변경
    - 권한: IsOwner
    """,
    'manual_parameters': [
        Parameter(
            name='user',
            description='의사 파일 객체의 pk',
            in_=IN_PATH,
            type=TYPE_INTEGER
        )
    ],
    'request_body': Schema(
        title='파일 수정',
        type=TYPE_OBJECT,
        properties={
            'file': doctor_file_schema['file'],
            'deleted': common_file_schema['deleted']
        },
        required=['file', 'deleted']
    ),
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'id': common_file_schema['id'],
                    'update_url': common_file_schema['update_url'],
                    'download_url': common_file_schema['download_url'],
                    'prescription': doctor_file_schema['prescription'],
                    'file': doctor_file_schema['file'],
                    'uploader': doctor_file_schema['uploader'],
                    'created_at': common_file_schema['created_at'],
                    'deleted': common_file_schema['deleted']
                }
            ),
            description='수정된 파일정보 출력',
            examples={
                'application/json': {
                    "id": "444a2710-f10a-4893-b7a8-5a7d6f336dbb",
                    "update_url": "http://127.0.0.1:8000/datafiles/doctor-files/444a2710-f10a-4893-b7a8-5a7d6f336dbb/update",
                    "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/444a2710-f10a-4893-b7a8-5a7d6f336dbb/download",
                    "prescription": 22,
                    "file": "2021-03-09/md/doctor1doctor.com_175027_2-1_모델_정리.md",
                    "uploader": 2,
                    "created_at": "2021-03-09T17:30:51.641123",
                    "deleted": "true"
                }
            }
        )
    }
}

patient_file_list = {
    'operation_summary': '[LIST] 환자가 올린 파일 리스트',
    'operation_description': """
    - 기능: 로그인한 환자 계정으로 올린 파일의 리스트를 출력
    - 권한: IsPatient
    """,
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_ARRAY,
                items=Schema(
                    type=TYPE_OBJECT,
                    properties={
                        'url': common_file_schema['url'],
                        'download_url': common_file_schema['download_url'],
                        'id': common_file_schema['id'],
                        'file_prescription': patient_file_schema['file_prescription'],
                        'file': patient_file_schema['file'],
                        'uploader': patient_file_schema['uploader'],
                        'uploader_name': common_file_schema['uploader_name'],
                        'created_at': common_file_schema['created_at'],
                    }
                )
            ),
            description='파일 리스트 출력',
            examples={
                'application/json': [
                    {
                        "url": "http://127.0.0.1:8000/datafiles/patient-files/aef86eb7-85f4-4c07-99f0-9916cebca56d/update",
                        "download_url": "http://127.0.0.1:8000/datafiles/patient-files/aef86eb7-85f4-4c07-99f0-9916cebca56d/download",
                        "id": "aef86eb7-85f4-4c07-99f0-9916cebca56d",
                        "file_prescription": 7,
                        "file": "http://127.0.0.1:8000/storage/2021-03-05/md/patient1patient.com_210509_test.md",
                        "uploader": 5,
                        "uploader_name": "환자일",
                        "created_at": "2021-03-05T21:05:09.231118"
                    },
                    {
                        "url": "http://127.0.0.1:8000/datafiles/patient-files/a5bbd51e-33fe-4c9e-88fe-c7a4cc336c51/update",
                        "download_url": "http://127.0.0.1:8000/datafiles/patient-files/a5bbd51e-33fe-4c9e-88fe-c7a4cc336c51/download",
                        "id": "a5bbd51e-33fe-4c9e-88fe-c7a4cc336c51",
                        "file_prescription": 7,
                        "file": "http://127.0.0.1:8000/storage/2021-03-05/md/patient1patient.com_203405_test_qZ6GCcW.md",
                        "uploader": 5,
                        "uploader_name": "환자일",
                        "created_at": "2021-03-05T20:34:05.959185"
                    },
                ]
            }
        )
    }
}

patient_file_create = {
    "operation_summary": "[CREATE] 환자 파일 업로드",
    "operation_description": """
    - 기능: 환자가 스케줄 객체(FilePrescription)에 파일 업로드 
    - 권한: IsPatient
    """,
    "request_body": Schema(
        title="파일 업로드",
        type=TYPE_OBJECT,
        properties={
            'file_prescription': patient_file_schema['file_prescription'],
            'file': patient_file_schema['file']
        },
        required=['file_prescription', 'file']
    ),
    "responses": {
        "201": Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': common_file_schema['url'],
                    'download_url': common_file_schema['download_url'],
                    'id': common_file_schema['id'],
                    'file_prescription': patient_file_schema['file_prescription'],
                    'file': patient_file_schema['file'],
                    'created_at': common_file_schema['created_at']
                }
            ),
            description="파일 업로드 결과",
            examples={
                'application/json': {
                    "url": "http://127.0.0.1:8000/datafiles/patient-files/18440b0b-b284-416b-8fee-ac4a06909666/update",
                    "download_url": "http://127.0.0.1:8000/datafiles/patient-files/18440b0b-b284-416b-8fee-ac4a06909666/download",
                    "id": "18440b0b-b284-416b-8fee-ac4a06909666",
                    "file_prescription": 248,
                    "file": "2021-03-09/md/patient1patient.com_180240_test.md",
                    "created_at": "2021-03-09T18:02:40.987617"
                }
            }
        )
    }
}

patient_file_detail = {
    "operation_summary": "[DETAIL] 환자 파일 세부 정보",
    "operation_description": """
    - 기능: 환자가 업로드한 파일의 세부 정보 출력(detail page)
    - 권한: IsOwner, CareDoctorReadOnly
    """,
    'manual_parameters': [
        Parameter(
            name='id',
            description='파일 객체의 pk(uuid)',
            in_=IN_PATH,
            type=TYPE_STRING,
            format=FORMAT_UUID
        )
    ],
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'update_url': common_file_schema['update_url'],
                    'download_url': common_file_schema['download_url'],
                    'id': common_file_schema['id'],
                    'prescription': doctor_file_schema['prescription'],
                    'file': doctor_file_schema['file'],
                    'uploader': doctor_file_schema['uploader'],
                    'created_at': common_file_schema['created_at'],
                    'uploader_name': common_file_schema['uploader_name']
                }
            ),
            description="환자가 올린 파일의 세부정보 출력",
            examples={
                'application/json': {
                    "url": "http://127.0.0.1:8000/datafiles/patient-files/36430d52-16a7-4f05-958b-eb8d4ca192b0",
                    "download_url": "http://127.0.0.1:8000/datafiles/patient-files/36430d52-16a7-4f05-958b-eb8d4ca192b0/download",
                    "id": "36430d52-16a7-4f05-958b-eb8d4ca192b0",
                    "file_prescription": 247,
                    "file": "http://127.0.0.1:8000/storage/2021-03-09/md/patient1patient.com_180903_test.md",
                    "uploader": 5,
                    "created_at": "2021-03-09T18:09:03.202569",
                    "uploader_name": "일환자"
                }
            }
        )
    }
}

patient_file_update = {
    'operation_summary': '[UPDATE] 환자 파일 정보 수정',
    'operation_description': """
    - 기능: 업로드된 파일 변경
    - 권한: IsOwner
    """,
    'manual_parameters': [
        Parameter(
            name='id',
            description='환자 파일 객체의 pk',
            in_=IN_PATH,
            type=TYPE_INTEGER
        )
    ],
    'request_body': Schema(
        title='파일 수정',
        type=TYPE_OBJECT,
        properties={
            'file_prescription': patient_file_schema['file_prescription'],
            'file': patient_file_schema['file']
        },
        required=['file_prescription']
    ),
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': common_file_schema['url'],
                    'download_url': common_file_schema['download_url'],
                    'id': common_file_schema['id'],
                    'file_prescription': patient_file_schema['file_prescription'],
                    'file': patient_file_schema['file'],
                    'uploader': patient_file_schema['uploader'],
                    'created_at': common_file_schema['created_at']
                }
            ),
            description='수정된 파일정보 출력',
            examples={
                'application/json': {
                    "url": "http://127.0.0.1:8000/datafiles/patient-files/36430d52-16a7-4f05-958b-eb8d4ca192b0",
                    "download_url": "http://127.0.0.1:8000/datafiles/patient-files/36430d52-16a7-4f05-958b-eb8d4ca192b0/download",
                    "id": "36430d52-16a7-4f05-958b-eb8d4ca192b0",
                    "file_prescription": 247,
                    "file": "http://127.0.0.1:8000/storage/2021-03-09/md/patient1patient.com_183151_test.md",
                    "uploader": 5,
                    "created_at": "2021-03-09T18:09:03.202569"
                }
            }
        )
    }
}
