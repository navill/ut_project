from drf_yasg.openapi import *

from accounts.docs import (doctor_path_parameter,
                           patient_path_parameter,
                           user_field_schema,
                           account_schema,
                           doctor_schema,
                           doctor_update_url_schema,
                           patient_schema,
                           patient_url_schema,
                           )
from files.docs import common_file_schema, doctor_file_schema, patient_file_schema
from prescriptions.docs import (prescription_path_parameter,
                                prescription_url_schema,
                                prescription_schema,
                                file_prescription_path_parameter,
                                file_prescription_url_schema,
                                file_prescription_schema,
                                )

doctor_with_patients = {
    'operation_summary': '[DETAIL][의사] 로그인 시 의사 정보 및 담당 환자의 리스트 출력',
    'operation_description': """
    - 기능: 의사 계정으로 로그인 했을 때 첫 번째 출력될 데이터표시
        - 의사 detail 정보
        - 환자 리스트: 의사 계정에 연결(related)된 환자의 리스트
    - 권한: IsOwner 
    """,
    'manual_parameters': [
        doctor_path_parameter
    ],
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': doctor_update_url_schema['url'],
                    'user': user_field_schema['id'],
                    'major': doctor_schema['major_name'],
                    'first_name': account_schema['first_name'],
                    'last_name': account_schema['last_name'],
                    'gender': account_schema['gender'],
                    'created_at': account_schema['created_at'],
                    'address': account_schema['address'],
                    'phone': account_schema['phone'],
                    'description': doctor_schema['description'],
                    'patients': Schema(
                        type=TYPE_ARRAY,
                        description='환자 객체 리스트',
                        items=Schema(
                            type=TYPE_OBJECT,
                            properties={
                                'url': patient_url_schema['url'],
                                'user': user_field_schema['id'],
                                'doctor': patient_schema['doctor'],
                                'birth': patient_schema['birth'],
                                'age': patient_schema['age'],
                                'first_name': account_schema['first_name'],
                                'last_name': account_schema['last_name'],
                                'gender': account_schema['gender'],
                                'created_at': account_schema['created_at'],
                            }
                        )
                    )
                },

            ),
            description='의사 정보 및 환자 리스트 출력',
            examples={
                'application/json': {
                    "url": "http://127.0.0.1:8000/accounts/doctors/2/update",
                    "user": 2,
                    "major": "정신의학",
                    "first_name": "의사",
                    "last_name": "일",
                    "gender": "남",
                    "created_at": "2021-01-27T13:09:58.512592",
                    "address": "광주",
                    "phone": "010-11-1234",
                    "description": "내용이 수정되었습니다.",
                    "profile_url": "http://127.0.0.1:8000/core-api/doctors/2/detail",
                    "patients": [
                        {
                            "url": "http://127.0.0.1:8000/accounts/patients/5",
                            "user": 5,
                            "doctor": 2,
                            "birth": "1988-04-24",
                            "age": 32,
                            "first_name": "환자",
                            "last_name": "일",
                            "gender": "남",
                            "created_at": "2021-01-27T13:12:08.560619"
                        },
                        {
                            "url": "http://127.0.0.1:8000/accounts/patients/6",
                            "user": 6,
                            "doctor": 2,
                            "birth": "1988-03-08",
                            "age": 33,
                            "first_name": "환자",
                            "last_name": "이",
                            "gender": "남",
                            "created_at": "2021-01-27T13:12:24.349006"
                        },
                    ]
                }
            }
        ),
    }
}

patient_with_prescriptions = {
    'operation_summary': '[DETAIL] 환자의 세부 정보 및 환자의 소견서 리스트 출력',
    'operation_description': """
    - 기능: 환자 리스트 중 특정 환자를 선택했을 때 보여질 내용 표시
        - 환자의 세부 정보
        - 환자를 대상으로 작성된 소견서 리스트
    - 권한: IsDoctor
    """,
    'manual_parameters': [
        patient_path_parameter
    ],
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'user': user_field_schema['id'],
                    'doctor': patient_schema['doctor'],
                    'birth': patient_schema['birth'],
                    'age': patient_schema['age'],
                    'first_name': account_schema['first_name'],
                    'last_name': account_schema['last_name'],
                    'gender': account_schema['gender'],
                    'created_at': account_schema['created_at'],
                    'phone': account_schema['phone'],
                    'emergency_call': patient_schema['emergency_call'],
                    'prescriptions': Schema(
                        type=TYPE_ARRAY,
                        description='소견서 리스트',
                        items=Schema(
                            type=TYPE_OBJECT,
                            properties={
                                'url': Schema(
                                    description='소견서 세부 정보 및 일정(file_prescriptions) url',
                                    type=TYPE_STRING,
                                    format=FORMAT_URI
                                ),
                                # **prescription_list_schema
                                'id': prescription_schema['id'],
                                'writer': prescription_schema['writer'],
                                'patient': prescription_schema['patient'],
                                'status': prescription_schema['status'],
                                'checked': prescription_schema['checked'],
                                'created_at': prescription_schema['created_at']
                            }
                        )
                    )
                },
            ),
            description='환자 세부 정보 및 환자의 소견서 출력',
            examples={
                'application/json': {
                    "user": 5,
                    "doctor": 2,
                    "birth": "1988-04-24",
                    "age": 32,
                    "first_name": "환자",
                    "last_name": "일",
                    "gender": "남",
                    "created_at": "2021-01-27T13:12:08.560619",
                    "address": "수정된 광주광역시",
                    "phone": "010-1212-1212",
                    "emergency_call": "010-2121-2121",
                    "prescriptions": [
                        {
                            "url": "http://127.0.0.1:8000/core-api/doctors/prescription-nested-files/23/file-prescriptions",
                            "id": 23,
                            "writer": 2,
                            "patient": 5,
                            "status": "알 수 없음",
                            "checked": "false",
                            "created_at": "2021-03-06T22:10:20.618187"
                        },
                        {
                            "url": "http://127.0.0.1:8000/core-api/doctors/prescription-nested-files/22/file-prescriptions",
                            "id": 22,
                            "writer": 2,
                            "patient": 5,
                            "status": "알 수 없음",
                            "checked": "false",
                            "created_at": "2021-03-06T22:06:45.844621"
                        },
                    ]
                }
            }
        ),
    }
}

prescription_with_file_prescription = {
    'operation_summary': '[DETAIL] 소견서에 등록된 파일 업로드 일정(FilePrescription)',
    'operation_description': """
    - 기능: 소견서 리스트 중 특정 소견서의 세부 사항 및 환자가 업로드 해야할 일정 표시 
        - 소견서 세부 정보
        - start_date ~ end_date에 매핑되는 file_prescription 리스트 
    - 권한: IsDoctor
    """,
    'manual_parameters': [
        prescription_path_parameter
    ],
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': prescription_url_schema['update_url'],
                    'id': prescription_schema['id'],
                    'writer': prescription_schema['writer'],
                    'patient': prescription_schema['patient'],
                    'status': prescription_schema['status'],
                    'checked': prescription_schema['checked'],
                    'created_at': prescription_schema['created_at'],
                    'updated_at': prescription_schema['updated_at'],
                    'description': prescription_schema['description'],
                    'start_date': prescription_schema['start_date'],
                    'end_date': prescription_schema['end_date'],
                    'doctor_files': Schema(
                        type=TYPE_ARRAY,
                        items=Schema(
                            type=TYPE_OBJECT,
                            properties={
                                'id': common_file_schema['id'],
                                'download_url': common_file_schema['download_url'],
                                'prescription': doctor_file_schema['prescription'],
                                'file': doctor_file_schema['file'],
                                'uploader': doctor_file_schema['uploader'],
                                'created_at': common_file_schema['created_at']
                            }
                        )
                    ),
                    'file_prescriptions': Schema(
                        type=TYPE_ARRAY,
                        items=Schema(
                            type=TYPE_OBJECT,
                            properties={
                                'id': file_prescription_schema['id'],
                                'prescription': file_prescription_schema['prescription'],
                                'uploaded': file_prescription_schema['uploaded'],
                                'checked': file_prescription_schema['checked'],
                                'date': file_prescription_schema['date'],
                                'status': file_prescription_schema['status'],
                                'created_at': file_prescription_schema['created_at'],
                                'updated_at': file_prescription_schema['updated_at'],
                            }
                        )
                    )
                },
            ),
            description='환자 세부 정보 및 환자의 소견서 출력',
            examples={
                'application/json': {
                    "url": "http://127.0.0.1:8000/prescriptions/23/update",
                    "id": 23,
                    "writer": 2,
                    "patient": 5,
                    "status": "알 수 없음",
                    "checked": "false",
                    "created_at": "2021-03-06T22:10:20.618187",
                    "updated_at": "2021-03-06T22:10:20.618222",
                    "description": "doctor2 test prescription",
                    "start_date": "2021-01-01",
                    "end_date": "2021-01-10",
                    "doctor_files": [
                        {
                            "id": "638b8c4f-a27e-4f19-86ba-a443c54cb907",
                            "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/638b8c4f-a27e-4f19-86ba-a443c54cb907/download",
                            "prescription": 23,
                            "file": "2021-03-06/md/doctor1doctor.com_221020_test_oTkswZ2.md",
                            "uploader": 2,
                            "created_at": "2021-03-06T22:10:20.836960"
                        },
                        {
                            "id": "c16f7176-8ebd-4222-992a-75ccda9f8778",
                            "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/c16f7176-8ebd-4222-992a-75ccda9f8778/download",
                            "prescription": 23,
                            "file": "2021-03-06/md/doctor1doctor.com_221020_test.md",
                            "uploader": 2,
                            "created_at": "2021-03-06T22:10:20.734439"
                        }
                    ],
                    "file_prescriptions": [
                        {
                            "url": "http://127.0.0.1:8000/core-api/doctors/file-prescriptions/247/patient-files",
                            "id": 247,
                            "prescription": 23,
                            "uploaded": "true",
                            "checked": "false",
                            "date": "2021-01-10",
                            "status": "알 수 없음",
                            "created_at": "2021-03-06T22:10:20.694952",
                            "updated_at": "2021-03-09T18:07:01.247296",

                        },
                        {
                            "url": "http://127.0.0.1:8000/core-api/doctors/file-prescriptions/246/patient-files",
                            "id": 246,
                            "prescription": 23,
                            "uploaded": "false",
                            "checked": "false",
                            "date": "2021-01-09",
                            "status": "알 수 없음",
                            "created_at": "2021-03-06T22:10:20.694919",
                            "updated_at": "2021-03-06T22:10:20.694925",
                        },
                    ]
                }
            }
        ),
    }
}

file_prescription_with_patient_file = {
    'operation_summary': '[DETAIL] 파일 업로드 일정(FilePrescription) 및 환자가 올린 파일 출력',
    'operation_description': """
    - 기능: 업로드 일정을 확인하거나, 환자가 업로드한 파일을 확인
    - 권한: IsOwner로 변경 예정
    - 내용
        - 업로드 일정 및 업로드된 파일에 대한 의사 소견
        - prescriptions: 대면 진료에 작성된 소견서
            - doctor_files: 의사가 올린 파일
        - patient_files: 환자가 올린 파일
    """,
    'manual_parameters': [
        file_prescription_path_parameter
    ],
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': file_prescription_url_schema['update_url'],
                    'id': file_prescription_schema['id'],
                    'prescriptions': Schema(
                        type=TYPE_ARRAY,
                        description='소견서 상세 정보',
                        items=Schema(
                            type=TYPE_OBJECT,
                            properties={
                                # **prescription_detail_schema
                                'id': prescription_schema['id'],
                                'writer': prescription_schema['writer'],
                                'patient': prescription_schema['patient'],
                                'status': prescription_schema['status'],
                                'checked': prescription_schema['checked'],
                                'created_at': prescription_schema['created_at'],
                                'updated_at': prescription_schema['updated_at'],
                                'description': prescription_schema['description'],
                                'start_date': prescription_schema['start_date'],
                                'end_date': prescription_schema['end_date']
                            }
                        )
                    ),
                    'uploaded': file_prescription_schema['uploaded'],
                    'checked': file_prescription_schema['checked'],
                    'date': file_prescription_schema['date'],
                    'status': file_prescription_schema['status'],
                    'created_at': file_prescription_schema['created_at'],
                    'updated_at': file_prescription_schema['updated_at'],
                    'description': file_prescription_schema['description'],
                    'day_number': file_prescription_schema['day_number'],
                    'active': file_prescription_schema['active'],
                    'patient_files': Schema(
                        type=TYPE_ARRAY,
                        description='환자가 올린 파일의 리스트',
                        items=Schema(
                            type=TYPE_OBJECT,
                            properties={
                                'url': common_file_schema['detail_url'],
                                'download_url': common_file_schema['download_url'],
                                'id': common_file_schema['id'],
                                'file': patient_file_schema['file'],
                                'uploader': patient_file_schema['uploader'],
                                'created_at': common_file_schema['created_at']
                            }
                        )
                    )
                },
            ),
            description='환자 세부 정보 및 환자의 소견서 출력',
            examples={
                'application/json': {
                    "url": "http://127.0.0.1:8000/prescriptions/file-pres/247",
                    "id": 247,
                    "prescription": {
                        "url": "http://127.0.0.1:8000/prescriptions/23/update",
                        "id": 23,
                        "writer": 2,
                        "patient": 5,
                        "status": "알 수 없음",
                        "checked": "false",
                        "created_at": "2021-03-06T22:10:20.618187",
                        "updated_at": "2021-03-06T22:10:20.618222",
                        "description": "doctor2 test prescription",
                        "start_date": "2021-01-01",
                        "end_date": "2021-01-10",
                        "doctor_files": [
                            {
                                "id": "638b8c4f-a27e-4f19-86ba-a443c54cb907",
                                "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/638b8c4f-a27e-4f19-86ba-a443c54cb907/download",
                                "prescription": 23,
                                "file": "2021-03-06/md/doctor1doctor.com_221020_test_oTkswZ2.md",
                                "uploader": 2,
                                "created_at": "2021-03-06T22:10:20.836960"
                            },
                            {
                                "id": "c16f7176-8ebd-4222-992a-75ccda9f8778",
                                "download_url": "http://127.0.0.1:8000/datafiles/doctor-files/c16f7176-8ebd-4222-992a-75ccda9f8778/download",
                                "prescription": 23,
                                "file": "2021-03-06/md/doctor1doctor.com_221020_test.md",
                                "uploader": 2,
                                "created_at": "2021-03-06T22:10:20.734439"
                            }
                        ]
                    },
                    "uploaded": "true",
                    "checked": "false",
                    "date": "2021-01-10",
                    "status": "알 수 없음",
                    "created_at": "2021-03-06T22:10:20.694952",
                    "updated_at": "2021-03-09T18:07:01.247296",
                    "description": "",
                    "day_number": 10,
                    "active": "true",
                    "patient_files": [
                        {
                            "url": "http://127.0.0.1:8000/datafiles/patient-files/36430d52-16a7-4f05-958b-eb8d4ca192b0",
                            "download_url": "http://127.0.0.1:8000/datafiles/patient-files/36430d52-16a7-4f05-958b-eb8d4ca192b0/download",
                            "id": "36430d52-16a7-4f05-958b-eb8d4ca192b0",
                            "file_prescription": 247,
                            "file": "null",
                            "uploader": 5,
                            "created_at": "2021-03-09T18:09:03.202569"
                        },
                        {
                            "url": "http://127.0.0.1:8000/datafiles/patient-files/0409cd28-e6ac-413d-937e-701bc63d15fe",
                            "download_url": "http://127.0.0.1:8000/datafiles/patient-files/0409cd28-e6ac-413d-937e-701bc63d15fe/download",
                            "id": "0409cd28-e6ac-413d-937e-701bc63d15fe",
                            "file_prescription": 247,
                            "file": "http://127.0.0.1:8000/storage/2021-03-09/md/patient1patient.com_180701_test.md",
                            "uploader": 5,
                            "created_at": "2021-03-09T18:07:01.230364"
                        }
                    ]
                }
            }
        ),
    }
}

uploaded_patient_file_history = {
    'operation_summary': '[LIST] 환자가 새로 업로드한 스케줄(FilePrescription) 리스트',
    'operation_description': """
    - 기능: 환자가 파일을 업로드했을 때 의사가 쉽게 확인할 수 있도록 업로드된 파일 리스트 표시
        ```python
        def filter_new_uploaded_file(self) -> 'FilePrescriptionQuerySet':
            return self.filter_uploaded().filter_not_checked()
        ```
        - 환자가 파일을 올렸지만 의사가 아직 확인하지 않은 상태를 리스트로 표시
    - 권한: IsDoctor
    """,
    'responses': {
        '200': Response(
            schema=Schema(
                title='환자가 파일을 새로 올렸을 때 출력될 리스트',
                type=TYPE_OBJECT,
                properties={
                    'url': Schema(
                        description='patient file을 포함한 file prescription detail url',
                        type=TYPE_STRING,
                        format=FORMAT_URI
                    ),
                    'id': file_prescription_schema['id'],
                    'prescription': file_prescription_schema['prescription'],
                    'uploaded': file_prescription_schema['uploaded'],
                    'checked': file_prescription_schema['checked'],
                    'date': file_prescription_schema['date'],
                    'status': file_prescription_schema['status'],
                    'created_at': file_prescription_schema['created_at']
                }
            ),
            description='의사가 확인하지 않은 업로드된 환자의 파일 리스트',
            examples={
                'application/json': [
                    {
                        "url": "http://127.0.0.1:8000/core-api/doctors/file-prescriptions/248/patient-files",
                        "id": 248,
                        "prescription": 3,
                        "uploaded": "true",
                        "checked": "false",
                        "date": "2021-03-07",
                        "status": "알 수 없음",
                        "created_at": "2021-03-06T22:17:09.097019"
                    },
                    {
                        "url": "http://127.0.0.1:8000/core-api/doctors/file-prescriptions/247/patient-files",
                        "id": 247,
                        "prescription": 23,
                        "uploaded": "true",
                        "checked": "false",
                        "date": "2021-01-10",
                        "status": "알 수 없음",
                        "created_at": "2021-03-06T22:10:20.694952"
                    },
                ]
            }
        )
    },

}

expired_file_prescription_history = {
    'operation_summary': '[LIST] 정해진 날짜에 환자가 파일을 올리지 않은 스케줄(FilePrescription) 리스트',
    'operation_description': """
    - 기능: uploaded=False 상태의 FilePrescription 객체 출력 
    ```python
    def filter_upload_date_expired(self) -> 'FilePrescriptionQuerySet':
          return self.filter(date__lt=datetime.date.today()).filter_not_checked().filter_not_uploaded()
    ```
        - 환자가 업로드 날짜에 파일을 올리지 않은 목록을 표시
        - 현재 날짜 보다 클 경우(미래) 제외, 현재 날짜 보다 작을 경우(과거) 체크
    - 권한: IsDoctor
    """,
    'responses': {
        '200': Response(
            schema=Schema(
                type=TYPE_OBJECT,
                properties={
                    'url': Schema(
                        description='patient file을 포함한 file prescription detail url',
                        type=TYPE_STRING,
                        format=FORMAT_URI
                    ),
                    'id': file_prescription_schema['id'],
                    'prescription': file_prescription_schema['prescription'],
                    'uploaded': file_prescription_schema['uploaded'],
                    'checked': file_prescription_schema['checked'],
                    'date': file_prescription_schema['date'],
                    'status': file_prescription_schema['status'],
                    'created_at': file_prescription_schema['created_at']
                }
            ),
            description='파일이 업로드되지 않은 FilePrescription list',
            examples={
                'application/json': [
                    {
                        "url": "http://127.0.0.1:8000/core-api/doctors/file-prescriptions/246/patient-files",
                        "id": 246,
                        "prescription": 23,
                        "uploaded": "false",
                        "checked": "false",
                        "date": "2021-01-09",
                        "status": "알 수 없음",
                        "created_at": "2021-03-06T22:10:20.694919"
                    },
                    {
                        "url": "http://127.0.0.1:8000/core-api/doctors/file-prescriptions/245/patient-files",
                        "id": 245,
                        "prescription": 23,
                        "uploaded": "false",
                        "checked": "false",
                        "date": "2021-01-08",
                        "status": "알 수 없음",
                        "created_at": "2021-03-06T22:10:20.694878"
                    },
                ]
            }
        )
    },
}
