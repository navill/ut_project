"""
객체 생성 시 필요한 요소 출력

MedicalCenter
- 의사가 계정 생성할 때 보여질 병원 정보 리스트
    - 병원 이름
Department
- 병원이 선택되었을 때 보여질 부서 리스트
    - 부서 이름
Major
- 부서가 선택되었을 때 보여질 전공 리스트
    - 전공 이름
doctor
- 의사 리스트를 출력해야할 때 보여질 리스트
    - 병원 정보
    - 의사 이름
    - 전공

patient
- 환자 리스트를 출력할 때 보여질 리스트
    - 환자 이름
    - 나이(birth)
    - 성별

prescription
- 환자가 특정되었을 때 보여질 소견서 리스트
    - 처방 내용
    -
file_prescription
- prescription이 특정되었을 때 보여질 file_prescription 리스트
    - 업로드 일정
    - 파일 업로드 여부


*** -> choice_views를 새로 생성하지 말고 기존의 app에서 query param(django filter)을 이용한 choices 필드 생성
"""
