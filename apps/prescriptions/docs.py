from drf_yasg import openapi

prescription_list = {
    'operation_summary': '[LIST] Prescription(소견서) 리스트',
    'operation_description': """
    - 기능: 접속한 계정에 관계된 소견서 리스트 출력
    - 권한: IsDoctor or IsPatient
    """,
    'responses': {
        '200': openapi.Response(
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(
                            description='prescription 객체의 pk',
                            type=openapi.TYPE_INTEGER
                        ),
                        'writer': openapi.Schema(
                            description='작성자(의사)의 pk',
                            type=openapi.TYPE_INTEGER
                        ),
                        'patient': openapi.Schema(
                            description='소견서 대상(환자)의 pk',
                            type=openapi.TYPE_INTEGER
                        ),
                        'status': openapi.Schema(
                            description='환자의 상태 표시(default: NONE)',
                            enum=['NONE', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
                            type=openapi.TYPE_STRING
                        ),
                        'checked': openapi.Schema(
                            description='스케줄(file-prescription)에 환자의 파일을 의사가 모두 확인했을 경우 true, 그렇지 않을 경우 false',
                            type=openapi.TYPE_BOOLEAN
                        ),
                        'created_at': openapi.Schema(
                            description='소견서 작성일',
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                        )
                    }
                )
            ),
            description='소견서 리스트',
            examples={
                "application/json":
                    [
                        {
                            "id": 18,
                            "writer": 2,
                            "patient": 5,
                            "status": "알 수 없음",
                            "checked": 'false',
                            "created_at": "2021-03-06T19:42:29.784135"
                        },
                        {
                            "id": 16,
                            "writer": 2,
                            "patient": 5,
                            "status": "알 수 없음",
                            "checked": 'false',
                            "created_at": "2021-03-06T17:42:44.273817"
                        },
                        {
                            "id": 15,
                            "writer": 2,
                            "patient": 5,
                            "status": "알 수 없음",
                            "checked": 'false',
                            "created_at": "2021-03-06T17:42:12.013165"
                        }
                    ]
            }
        )
    }
}
prescription_create = {
    'operation_summary': '[CREATE] 소견서 작성',
    'operation_description': """
    - 기능: 환자에 대한 소견서를 작성.
        - prescription 생성 시, FilePrescription(환자 파일 업로드 일정), DoctorFile(의사가 올린 파일) 객체도 함께 생성된다.
    - 권한: IsDoctor
    """,
    'request_body': openapi.Schema(
        title='소견서 작성',
        type=openapi.TYPE_OBJECT,
        properties={
            'patient': openapi.Schema(
                description='환자 객체의 pk',
                type=openapi.TYPE_INTEGER
            ),
            'status': openapi.Schema(
                description='환자의 상태 표시(default: NONE)',
                enum=['NONE', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
                type=openapi.TYPE_STRING
            ),
            'start_date': openapi.Schema(
                format=openapi.FORMAT_DATE,
                description='파일 업로드 시작일',
                type=openapi.TYPE_STRING
            ),
            'end_date': openapi.Schema(
                format=openapi.FORMAT_DATE,
                description='파일 업로드 종료일',
                type=openapi.TYPE_STRING
            ),
            'doctor_upload_files': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description='의사가 올릴 파일',
                items=openapi.Schema(
                    type=openapi.TYPE_FILE
                )
            )
        },
        required=['patient', 'status', 'start_date', 'end_date']
    ),
    'responses': {
        '201': openapi.Response(
            schema=openapi.Schema(type=openapi.TYPE_OBJECT,
                                  properties={
                                      'url': openapi.Schema(
                                          type=openapi.TYPE_STRING,
                                          format=openapi.FORMAT_URI,
                                          description='detail url'
                                      ),
                                      'id': openapi.Schema(
                                          type=openapi.TYPE_INTEGER,
                                          description='생성된 객체의 pk'
                                      ),
                                      'status': openapi.Schema(
                                          description='환자의 상태 표시(default: NONE)',
                                          enum=['NONE', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
                                          type=openapi.TYPE_STRING
                                      ),
                                      'checked': openapi.Schema(
                                          description='환자가 올린 파일을 의사가 확인했는지 여부',
                                          type=openapi.TYPE_BOOLEAN
                                      ),
                                      'created_at': openapi.Schema(
                                          description='객체 생성일',
                                          type=openapi.TYPE_STRING,
                                          format=openapi.FORMAT_DATETIME
                                      ),
                                      'updated_at': openapi.Schema(
                                          description='객체 수정일',
                                          type=openapi.TYPE_STRING,
                                          format=openapi.FORMAT_DATETIME
                                      ),
                                      'start_date': openapi.Schema(
                                          format=openapi.FORMAT_DATE,
                                          description='파일 업로드 시작일',
                                          type=openapi.TYPE_STRING
                                      ),
                                      'end_date': openapi.Schema(
                                          format=openapi.FORMAT_DATE,
                                          description='파일 업로드 종료일',
                                          type=openapi.TYPE_STRING
                                      ),

                                      'doctor_files': openapi.Schema(
                                          type=openapi.TYPE_ARRAY,
                                          description='의사가 올린 파일 리스트',
                                          items=openapi.Schema(
                                              type=openapi.TYPE_OBJECT,
                                              properties={
                                                  'url': openapi.Schema(
                                                      type=openapi.TYPE_STRING,
                                                      format=openapi.FORMAT_URI,
                                                      description='파일 detail url'
                                                  ),
                                                  'download_url': openapi.Schema(
                                                      type=openapi.TYPE_STRING,
                                                      format=openapi.FORMAT_URI,
                                                      description='파일 다운로드 url'
                                                  ),
                                                  'file': openapi.Schema(
                                                      type=openapi.TYPE_FILE,
                                                      description='파일 객체'
                                                  ),
                                                  'created_at': openapi.Schema(
                                                      type=openapi.TYPE_STRING,
                                                      format=openapi.FORMAT_DATETIME,
                                                      description='파일 업로드 시간'
                                                  )
                                              }
                                          )
                                      ),
                                  }),
            description='소견서 작성 완료',
            examples={
                "application/json": {
                    "url": "http://127.0.0.1:8000/prescriptions/16",
                    "id": 16,
                    "status": "UNKNOWN",
                    "checked": 'false',
                    "created_at": "2021-03-06T17:42:44.273817",
                    "description": "doctor2 test prescription",
                    "updated_at": "2021-03-06T17:42:44.273845",
                    "start_date": "2021-01-01",
                    "end_date": "2021-01-10",
                }
            }
        ),

    }
}

prescription_update_propoerties = {
    'status': openapi.Schema(
        description='파일을 기반으로한 환자의 상태 표시(default: None)',
        enum=['None', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
        type=openapi.TYPE_STRING,
    ),
    'description': openapi.Schema(
        description='환자가 올린 파일을 의사가 분석하여 작성한 소견 내용',
        type=openapi.TYPE_STRING,
    ),
    'start_date': openapi.Schema(
        description='파일 업로드 시작일',
        type=openapi.TYPE_STRING
    ),
    'end_date': openapi.Schema(
        description='파일 업로드 종료일',
        type=openapi.TYPE_STRING
    )
}
prescription_update = {
    'operation_summary': '[UPDATE] 소견서 수정',
    'operation_description': """
    - 기능: 작성된 소견서의 세부사항 수정
    - 권한: IsOwner
    """,
    'manual_parameters': [
        openapi.Parameter(
            name='id',
            description='Prescription 객체의 pk',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER
        )
    ],
    'request_body': openapi.Schema(
        title='소견서 수정',
        type=openapi.TYPE_OBJECT,
        properties=prescription_update_propoerties,
        required=['status', 'active', 'description'],
    ),
    'responses': {
        '200': openapi.Response(
            schema=openapi.Schema(
                title='Prescription 수정 결과',
                type=openapi.TYPE_OBJECT,
                properties=prescription_update_propoerties
            ),
            description='prescription 수정 결과',
            examples={
                'application/json': {
                    "status": "UNKNOWN",
                    "description": "update prescription",
                    "start_date": "2021-01-01",
                    "end_date": "2021-01-06",
                }
            }
        )
    },
}

prescription_detail = {
    'operation_summary': '[DETAIL] 소견서 세부사항',
    'operation_description': """
    - 기능: 작성된 소견서의 세부사항 확인
    - 권한: IsOwner or RelatedPatientReadOnly
    """,
    'manual_paramters': prescription_update['manual_parameters'],
    'responses': prescription_update['responses'],
}

file_prescription_list = {
    'operation_summary': '[LIST] FilePrescription 리스트',
    'operation_description': """
    **FilePrescription: 환자가 올린 파일에 대한 소견 및 일부 정보를 담고있는 객체** 
    - 기능: 파일 업로드 관련 정보의 리스트를 출력
        - 로그인한 의사 계정으로 작성한 prescription(소견서)와 연결된 file prescription 리스트
    - 권한: IsDoctor
    """,
    'responses': {
        '200': openapi.Response(
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(
                        description='FilePrescription(파일 업로드 스케줄) 객체의 pk',
                        type=openapi.TYPE_INTEGER,
                    ),
                    'prescription': openapi.Schema(
                        description='Prescription(소견서) 객체의 pk',
                        type=openapi.TYPE_INTEGER,
                    ),
                    'uploaded': openapi.Schema(
                        description='환자가 파일을 올렸는지 여부',
                        type=openapi.TYPE_BOOLEAN,
                    ),
                    'checked': openapi.Schema(
                        description='의사가 환자 파일을 확인했는지 여부',
                        type=openapi.TYPE_BOOLEAN,
                    ),
                    'date': openapi.Schema(
                        description='환자가 업로드해야할 날짜',
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATE
                    ),
                    'status': openapi.Schema(
                        description='파일을 기반으로한 환자의 상태 표시',
                        enum=['None', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
                        type=openapi.TYPE_STRING,
                    ),
                    'created_at': openapi.Schema(
                        description='객체 생성일',
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATETIME
                    ),
                    'updated_at': openapi.Schema(
                        description='객체 수정일',
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATETIME
                    ),
                }
            ),
            description='의사가 지정한 업로드 일정에 대한 정보',
            examples={
                'application/json':
                    [
                        {
                            "id": 188,
                            "prescription": 18,
                            "uploaded": 'false',
                            "checked": 'false',
                            "date": "2021-01-10",
                            "status": "알 수 없음",
                            "created_at": "2021-03-06T19:42:29.805164",
                            "updated_at": "2021-03-06T19:42:29.805170"
                        },
                        {
                            "id": 187,
                            "prescription": 18,
                            "uploaded": 'false',
                            "checked": 'false',
                            "date": "2021-01-09",
                            "status": "알 수 없음",
                            "created_at": "2021-03-06T19:42:29.805127",
                            "updated_at": "2021-03-06T19:42:29.805134"
                        },
                        {
                            "id": 186,
                            "prescription": 18,
                            "uploaded": 'false',
                            "checked": 'false',
                            "date": "2021-01-08",
                            "status": "알 수 없음",
                            "created_at": "2021-03-06T19:42:29.805090",
                            "updated_at": "2021-03-06T19:42:29.805097"
                        }
                    ]
            }
        )
    }
}

file_prescription_update_properties = {
    'status': openapi.Schema(
        description='파일을 기반으로한 환자의 상태 표시',
        enum=['None', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
        type=openapi.TYPE_STRING,
    ),
    'active': openapi.Schema(
        description='스케줄 활성화 여부',
        type=openapi.TYPE_BOOLEAN,
    ),
    'checked': openapi.Schema(
        description='의사가 환자 파일을 확인했는지 여부',
        type=openapi.TYPE_BOOLEAN,
    ),
    'description': openapi.Schema(
        description='환자가 올린 파일을 의사가 분석하여 작성한 소견 내용',
        type=openapi.TYPE_STRING,
    ),
}

file_prescription_update = {
    'operation_summary': "[UPDATE] FilePrescription 세부 정보 수정",
    'operation_description': """
    - 기능: file prescription 객체의 세부 정보 수정
    - 권한: IsOwner(읽기 & 수정)
    """,
    'manual_parameters': [
        openapi.Parameter(
            name='id',
            description='FilePrescription 객체의 pk',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        )
    ],
    'request_body': openapi.Schema(
        title='FilePrescription 수정',
        type=openapi.TYPE_OBJECT,
        properties=file_prescription_update_properties,
        required=['status', 'active', 'checked', 'description'],
    ),
    'responses': {
        '201': openapi.Response(
            schema=openapi.Schema(
                title='FilePrescription 수정 결과',
                type=openapi.TYPE_OBJECT,
                properties=file_prescription_update_properties),
            description='FilePrescription 수정 완료',
            examples={
                'application/json': {
                    "status": "NONE",
                    "active": 'true',
                    "checked": 'true',
                    "description": "updated file prescription"
                }
            }
        )
    },
}

file_prescription_detail_properties = {
    'url': openapi.Schema(
        description='detail url',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_URI
    ),
    'id': openapi.Schema(
        description='FilePrescription(파일 업로드 스케줄) 객체의 pk',
        type=openapi.TYPE_INTEGER,
    ),
    'prescription': openapi.Schema(
        description='Prescription(소견서) 객체의 pk',
        type=openapi.TYPE_INTEGER,
    ),
    'uploaded': openapi.Schema(
        description='환자가 파일을 올렸는지 여부',
        type=openapi.TYPE_BOOLEAN,
    ),
    'checked': openapi.Schema(
        description='의사가 환자 파일을 확인했는지 여부',
        type=openapi.TYPE_BOOLEAN,
    ),
    'date': openapi.Schema(
        description='업로드 날짜',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE
    ),
    'status': openapi.Schema(
        description='파일을 기반으로한 환자의 상태 표시',
        enum=['None', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
        type=openapi.TYPE_STRING,
    ),
    'created_at': openapi.Schema(
        description='객체 생성일',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATETIME
    ),
    'updated_at': openapi.Schema(
        description='객체 수정일',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATETIME
    ),
    'description': openapi.Schema(
        description='환자가 올린 파일을 의사가 분석하여 작성한 소견 내용',
        type=openapi.TYPE_STRING,
    ),
    'day_number': openapi.Schema(
        description='파일 업로드 몇 번째 날짜인지 표시',
        type=openapi.TYPE_INTEGER,
    ),
    'active': openapi.Schema(
        description='파일 업로드 가능 여부',
        type=openapi.TYPE_BOOLEAN
    ),
    'deleted': openapi.Schema(
        description='일정이 지났거나 관리자에 의해 삭제된 스케줄인지 여부',
        type=openapi.TYPE_BOOLEAN
    )
}

file_prescription_detail = {
    'operation_summary': "[DETAIL] FilePrescription 세부 정보 접근",
    'operation_description': """
    - 기능: file prescription 객체의 세부 정보 접근
    - 권한: IsOwner or RelatedPatientReadOnly
    """,
    'manual_parameters': [
        openapi.Parameter(
            name='id',
            description='FilePrescription 객체의 pk',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        )
    ],
    'responses': {
        '200': openapi.Response(
            schema=openapi.Schema(type=openapi.TYPE_OBJECT,
                                  properties=file_prescription_detail_properties),
            description='환자가 올린 파일 기반 소견서',
            examples={
                'example': 'empty'
            }
        )
    },
}

file_prescription_create = {
    'operation_summary': '[CREATE] FilePrescription 객체 생성',
    'operation_description': """
    - 기능: file prescription 객체를 생성하는 end point
        - 보통은 prescription이 생성될 때 자동으로 생성되며, 의도적으로 file prescription 객체를 생성해야할 때 사용
    - 권한: IsDoctor
    """,
    'request_body': openapi.Schema(
        title='FilePrescription 객체 생성',
        type=openapi.TYPE_OBJECT,
        properties={
            'prescrition': openapi.Schema(
                description='소견서(Prescription 객체)의 pk',
                type=openapi.TYPE_INTEGER
            ),
            'description': openapi.Schema(
                description='의사가 환자의 파일을 확인한 후 파일에 대해 작성한 소견',
                type=openapi.TYPE_STRING
            ),
            'status': openapi.Schema(
                description='의사가 환자의 파일을 확인한 후 건강 상태를 표시(default=NONE)',
                enum=['NONE', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
                type=openapi.TYPE_STRING,
            ),
            'date': openapi.Schema(
                description='업로드 날짜',
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            'day_number': openapi.Schema(
                description='업로드 날짜 중 몇번째 일인지 표시',
                type=openapi.TYPE_INTEGER
            ),
            'checked': openapi.Schema(
                description='의사가 환자의 파일을 확인했는지 여부',
                type=openapi.TYPE_BOOLEAN
            )
        }
    ),
    'responses': {
        201: openapi.Response(
            schema=openapi.Schema(type=openapi.TYPE_OBJECT,
                                  properties=file_prescription_detail_properties
                                  ),
            description='file prescription 객체 생성 완료',
            examples={
                "application/json": {
                    "url": "http://127.0.0.1:8000/prescriptions/file-pres/190",
                    "id": 190,
                    "prescription": 3,
                    "description": "test file prescription",
                    "status": "UNKNOWN",
                    "day_number": 1,
                    "date": 'null',
                    "deleted": 'false',
                    "active": 'true',
                    "uploaded": 'false',
                    "checked": 'false',
                    "created_at": "2021-03-06T21:15:54.790759",
                    "updated_at": "2021-03-06T21:15:54.790781"
                }
            }
        )
    },
}
