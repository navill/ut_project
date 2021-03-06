from drf_yasg import openapi

prescription_path_parameter = openapi.Parameter(
    name='id',
    description='소견서(prescription) 객체의 pk',
    in_=openapi.IN_PATH,
    type=openapi.TYPE_INTEGER
)

prescription_url_schema = {
    'url': openapi.Schema(
        description='prescription detail url',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_URI
    ),
    'update_url': openapi.Schema(
        description='prescription update url',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_URI
    )
}
prescription_query_parameters = {
    'id': openapi.Parameter(
        name='id',
        description='소견서 객체의 id',
        type=openapi.TYPE_INTEGER,
        in_=openapi.IN_QUERY
    ),
    'writer_id': openapi.Parameter(
        name='writer_id',
        description="작성자(의사) 계정의 id",
        type=openapi.TYPE_INTEGER,
        in_=openapi.IN_QUERY,
    ),
    'patient_id': openapi.Parameter(
        name='patient_id',
        description="소견서 대상(환자) 계정의 id",
        type=openapi.TYPE_INTEGER,
        in_=openapi.IN_QUERY,
    ),
    'writer_name': openapi.Parameter(
        name='writer_name',
        description="작성자(의사)의 이름",
        type=openapi.TYPE_INTEGER,
        in_=openapi.IN_QUERY,
    ),
    'patient_name': openapi.Parameter(
        name='patient_name',
        description="환자의 이름",
        type=openapi.TYPE_STRING,
        in_=openapi.IN_QUERY,
    ),
    'start_date': openapi.Parameter(
        name='start_date',
        description="파일 업로드 시작일",
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        in_=openapi.IN_QUERY
    ),
    'end_date': openapi.Parameter(
        name='end_date',
        description='파일 업로드 종료일',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        in_=openapi.IN_QUERY
    ),
    'created_at': openapi.Parameter(
        name='created_at',
        description="소견서 작성 날짜(시간 제외)",
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        in_=openapi.IN_QUERY,
    ),
    'checked': openapi.Parameter(
        name='checked',
        description="의사가 기간내에 환자가 올린 파일을 모두 체크했는지 여부(prescription과 연결된 file_prescription객체 모두 체크(True) 했을 경우, True)",
        type=openapi.TYPE_STRING,
        enum=['True', 'False'],
        format=openapi.TYPE_BOOLEAN,
        in_=openapi.IN_QUERY,
    ),
    'status': openapi.Parameter(
        name='status',
        description="대면 진료 시 환자의 상태",
        type=openapi.TYPE_STRING,
        in_=openapi.IN_QUERY,
    ),
    'ordering': openapi.Parameter(
        name='ordering',
        description=
        """Prescription 객체의 필드를 기반으로 정렬.\n    
    ex) id를 기반으로 정렬할 경우 ordering=id(오름차순), ordering=-id(내림차순)
        """,
        type=openapi.TYPE_STRING,
        in_=openapi.IN_QUERY
    )

}
prescription_choice_schema = {
    'writer_name': openapi.Schema(
        description='소견서를 작성한 의사의 이름',
        type=openapi.TYPE_STRING
    ),
    'patient_name': openapi.Schema(
        description='환자의 이름',
        type=openapi.TYPE_STRING
    ),
}
prescription_schema = {
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
    ),
    "updated_at": openapi.Schema(
        description='소견서 수정일',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATETIME
    ),
    "description": openapi.Schema(
        description='의사가 작성한 소견서 내용',
        type=openapi.TYPE_STRING
    ),
    "start_date": openapi.Schema(
        description='환자가 올려야할 파일 일정 시작일',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE
    ),
    "end_date": openapi.Schema(
        description='환자가 올려야할 파일 일정 종료일',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE
    ),
}
prescription_list_schema = {
    'id': prescription_schema['id'],
    'writer': prescription_schema['writer'],
    'patient': prescription_schema['patient'],
    'status': prescription_schema['status'],
    'checked': prescription_schema['checked'],
    'created_at': prescription_schema['created_at']
}

prescription_detail_schema = {
    **prescription_list_schema,
    'updated_at': prescription_schema['updated_at'],
    'description': prescription_schema['description'],
    'start_date': prescription_schema['start_date'],
    'end_date': prescription_schema['end_date']
}

file_prescription_path_parameter = openapi.Parameter(
    name='id',
    description='file prescription 객체의 pk',
    in_=openapi.IN_PATH,
    type=openapi.TYPE_INTEGER
)
file_prescription_query_parameters = {
    'prescription_id': openapi.Parameter(
        name='prescription_id',
        description='Prescription 객체의 id',
        type=openapi.TYPE_INTEGER,
        in_=openapi.IN_QUERY
    ),
    'writer_id': openapi.Parameter(
        name='writer_id',
        description="작성자(의사) 계정의 id",
        type=openapi.TYPE_INTEGER,
        in_=openapi.IN_QUERY,
    ),
    'writer_name': openapi.Parameter(
        name='writer_name',
        description="작성자(의사) 이름",
        type=openapi.TYPE_STRING,
        in_=openapi.IN_QUERY,
    ),
    'patient_id': openapi.Parameter(
        name='patient_id',
        description="소견서 대상(환자) 계정의 id",
        type=openapi.TYPE_INTEGER,
        in_=openapi.IN_QUERY,
    ),
    'patient_name': openapi.Parameter(
        name='patient_name',
        description="소견서 대상(환자) 이름",
        type=openapi.TYPE_STRING,
        in_=openapi.IN_QUERY,
    ),
    'uploaded': openapi.Parameter(
        name='uploaded',
        description='환자가 파일을 올렸는지 여부',
        type=openapi.TYPE_BOOLEAN,
        in_=openapi.IN_QUERY
    ),
    'status': openapi.Parameter(
        name='status',
        description='파일을 확인한 의사가 저장한 환자의 상태',
        type=openapi.TYPE_STRING,
        enum=['NONE', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
        in_=openapi.IN_QUERY
    ),
    'date': openapi.Parameter(
        name='date',
        description="파일 업로드 날짜",
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        in_=openapi.IN_QUERY
    ),
    'created_at': openapi.Parameter(
        name='created_at',
        description="소견서 작성 날짜(시간 제외)",
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        in_=openapi.IN_QUERY,
    ),
    'checked': openapi.Parameter(
        name='checked',
        description="의사가 기간내에 환자가 올린 파일을 모두 체크했는지 여부(prescription과 연결된 file_prescription객체 모두 체크(True) 했을 경우, True)",
        type=openapi.TYPE_STRING,
        format=openapi.TYPE_BOOLEAN,
        in_=openapi.IN_QUERY,
    ),
    'active': openapi.Parameter(
        name='active',
        description='파일 업로드 일정 활성화 여부',
        type=openapi.TYPE_STRING,
        in_=openapi.IN_QUERY,
    ),
    'ordering': openapi.Parameter(
        name='ordering',
        description=
        """FilePrescription 객체의 필드를 기반으로 정렬.\n    
    ex) id를 기반으로 정렬할 경우 ordering=id(오름차순), ordering=-id(내림차순)
        """,
        type=openapi.TYPE_STRING,
        in_=openapi.IN_QUERY
    )
}
file_prescription_schema = {
    'id': openapi.Schema(
        description='file prescription 객체의 pk',
        type=openapi.TYPE_INTEGER
    ),
    'prescription': openapi.Schema(
        description='소견서(prescription) 객체의 pk',
        type=openapi.TYPE_INTEGER
    ),
    'uploaded': openapi.Schema(
        description='환자가 파일을 올렸는지 여부',
        type=openapi.TYPE_BOOLEAN
    ),
    'checked': openapi.Schema(
        description='환자의 파일을 의사가 확인했는지 여부',
        type=openapi.TYPE_BOOLEAN
    ),
    'date': openapi.Schema(
        description='소견서 작성 시 생성된 일정에 맵핑되는 날짜(1일~3일일 경우 각 날짜에 해당하는 file_prescription 객체가 생성됨)',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE
    ),
    'status': openapi.Schema(
        description='환자의 상태 표시(default: NONE)',
        enum=['NONE', 'NORMAL', 'ABNORMAL', 'UNKNOWN'],
        type=openapi.TYPE_STRING
    ),
    'created_at': openapi.Schema(
        description='소견서 작성일(소견서 작성시 file prescription 생성)',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATETIME,
    ),
    "updated_at": openapi.Schema(
        description='객체 수정일',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATETIME
    ),
    "description": openapi.Schema(
        description='환자가 올린 파일을 바탕으로 의사가 작성한 소견서 내용',
        type=openapi.TYPE_STRING
    ),
    'day_number': openapi.Schema(
        description='몇 번째 날짜인지 표시',
        type=openapi.TYPE_INTEGER,
    ),
    'active': openapi.Schema(
        description='업로드 일정 활성화 여부',
        type=openapi.TYPE_BOOLEAN
    ),
}
file_prescription_choice_schema = {
    'writer_id': openapi.Schema(
        description='스케줄 등록자(의사)의 id',
        type=openapi.TYPE_INTEGER
    ),
    "writer_name": openapi.Schema(
        description='스케줄 등록자(의사)의 이름',
        type=openapi.TYPE_STRING,
    ),
    "patient_id": openapi.Schema(
        description='환자 계정의 id',
        type=openapi.TYPE_INTEGER
    ),
    'patient_name': openapi.Schema(
        description='환자의 이름',
        type=openapi.TYPE_STRING,
    ),
}

file_prescription_url_schema = {
    'url': openapi.Schema(
        description='file prescription detail url',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_URI
    ),
    'update_url': openapi.Schema(
        description='file prescription update url',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_URI
    )
}
file_prescription_list_schema = {
    'id': file_prescription_schema['id'],
    'prescription': file_prescription_schema['prescription'],
    'uploaded': file_prescription_schema['uploaded'],
    'checked': file_prescription_schema['checked'],
    'date': file_prescription_schema['date'],
    'status': file_prescription_schema['status'],
    'created_at': file_prescription_schema['created_at']
}

file_prescription_detail_schema = {
    **file_prescription_list_schema,
    'updated_at': file_prescription_schema['updated_at'],
    'description': file_prescription_schema['description'],
    'day_number': file_prescription_schema['day_number'],
    'active': file_prescription_schema['active'],
}

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
                        **prescription_list_schema,
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
    'manual_parameters': prescription_update['manual_parameters'],
    'responses': {
        '200': openapi.Response(
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={**prescription_detail_schema}
            ),
            description='소견서 세부 사항',
            examples={
                'application/json': {
                    "id": 23,
                    "writer": 2,
                    "patient": 5,
                    "status": "알 수 없음",
                    "checked": "false",
                    "created_at": "2021-03-06T22:10:20.618187",
                    "updated_at": "2021-03-06T22:10:20.618222",
                    "description": "doctor2 test prescription",
                    "start_date": "2021-01-01",
                    "end_date": "2021-01-10"
                }
            }
        )
    },
}
prescription_choice = {
    'operation_summary': '[LIST-CHOICE] Prescription 선택 리스트',
    'operation_description': """
    - 기능: 소견서에 대한 최소한의 정보를 출력하며, 주어진 필드를 통해 필터링 가능
        - 범위 검색 필드: [created_at, start_date, end_date]
        - 공통 lookup postfix: [exact, lte, gte] \n
        [example] \n
        ```...?created_at=2021-01-03&created_at_lookup=exact```\n
        => 2021-01-03일에 작성된 모든 소견서 출력 
    - 권한: IsDoctor
    """,
    "manual_parameters": [
        *prescription_query_parameters.values()
    ],
    'responses': {
        '200': openapi.Response(
            schema=openapi.Schema(
                title='Prescription 필터링 결과',
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': prescription_schema['id'],
                    'writer_id': prescription_schema['writer'],
                    'patient_id': prescription_schema['patient'],
                    'writer_name': prescription_choice_schema['writer_name'],
                    'patient_name': prescription_choice_schema['patient_name'],
                    'status': prescription_schema['status'],
                    'checked': prescription_schema['checked'],
                    'created_at': prescription_schema['created_at']
                }
            ),
            description='prescription 수정 결과',
            examples={
                'application/json':
                    [
                        {
                            "id": 23,
                            "writer_id": 2,
                            "patient_id": 5,
                            "writer_name": "일의사",
                            "patient_name": "삼환자",
                            "start_date": "2021-01-06",
                            "end_date": "2021-01-20",
                            "created_at": "2021-03-06T22:10:20.618187",
                            "status": "알 수 없음",
                            "checked": "false"
                        },
                        {
                            "id": 22,
                            "writer_id": 2,
                            "patient_id": 6,
                            "writer_name": "일의사",
                            "patient_name": "이환자",
                            "start_date": "2021-03-06",
                            "end_date": "2021-03-10",
                            "created_at": "2021-03-06T22:06:45.844621",
                            "status": "알 수 없음",
                            "checked": "false"
                        },
                        {
                            "id": 21,
                            "writer_id": 2,
                            "patient_id": 7,
                            "writer_name": "일의사",
                            "patient_name": "일환자",
                            "start_date": "2021-03-01",
                            "end_date": "2021-03-06",
                            "created_at": "2021-03-06T22:05:38.261055",
                            "status": "정상",
                            "checked": "true"
                        }
                    ],
            },

        )
    },

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
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
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
                    })
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

file_prescription_choice = {
    'operation_summary': '[LIST-CHOICE] FilePrescription 선택 리스트',
    'operation_description': """
    - 기능: FilePrescription에 대한 최소한의 정보를 출력하며, 주어진 필드를 통해 필터링 가능
        - 범위 검색 필드: [created_at, date]
        - 공통 lookup postfix: [exact, lte, gte] \n
        [example] \n
        ```...?created_at=2021-01-03&created_at_lookup=exact```: 2021년 1월 3일날 작성된 소견서 리스트\n
        ```...?created_at=2021-01-03&created_at_lookup=gte```: 2021년 1월 3일부터 작성된 소견서 리스트\n
    - 권한: IsDoctor
    """,
    "manual_parameters": [
        *file_prescription_query_parameters.values()
    ],
    'responses': {
        '200': openapi.Response(
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": file_prescription_schema['id'],
                    "prescription_id": file_prescription_schema['prescription'],
                    "writer_id": file_prescription_choice_schema['writer_id'],
                    "writer_name": file_prescription_choice_schema['writer_name'],
                    "patient_id": file_prescription_choice_schema['patient_id'],
                    "patient_name": file_prescription_choice_schema['patient_name'],
                    "status": file_prescription_schema['status'],
                    "checked": file_prescription_schema['checked'],
                    "created_at": file_prescription_schema['created_at'],
                    "day_number": file_prescription_schema['day_number'],
                    "date": file_prescription_schema['date'],
                    "uploaded": file_prescription_schema['uploaded']
                }
            ),
            description='file prescription 필터링 결과',
            examples={
                'application/json':
                    [
                        {
                            "id": 248,
                            "prescription_id": 3,
                            "writer_id": 2,
                            "writer_name": "일의사",
                            "patient_id": 5,
                            "patient_name": "일환자",
                            "status": "UNKNOWN",
                            "checked": "false",
                            "created_at": "2021-03-06T22:17:09.097019",
                            "day_number": 1,
                            "date": "2021-03-07",
                            "uploaded": "true"
                        },
                        {
                            "id": 247,
                            "prescription_id": 23,
                            "writer_id": 2,
                            "writer_name": "일의사",
                            "patient_id": 5,
                            "patient_name": "일환자",
                            "status": "UNKNOWN",
                            "checked": "false",
                            "created_at": "2021-03-06T22:10:20.694952",
                            "day_number": 10,
                            "date": "2021-01-10",
                            "uploaded": "true"
                        },
                        {
                            "id": 246,
                            "prescription_id": 23,
                            "writer_id": 2,
                            "writer_name": "일의사",
                            "patient_id": 5,
                            "patient_name": "일환자",
                            "status": "UNKNOWN",
                            "checked": "false",
                            "created_at": "2021-03-06T22:10:20.694919",
                            "day_number": 9,
                            "date": "2021-01-09",
                            "uploaded": "false"
                        }
                    ],
            },

        )
    },
}
