from collections import ChainMap
from typing import Type, Optional, TYPE_CHECKING

from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from accounts.models import Patient
from core.api.fields import PrescriptionFields, FilePrescriptionFields
from files.api.serializers import PatientUploadedFileListSerializer, DoctorFileInPrescriptionSerializer
from prescriptions.api.mixins import PrescriptionSerializerMixin
from prescriptions.models import Prescription, HealthStatus, FilePrescription

if TYPE_CHECKING:
    from django.db.models import QuerySet


class FilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, target_field: str = None, **kwargs):
        super().__init__(**kwargs)
        self.target_field = target_field

    def get_queryset(self) -> Optional[Type['QuerySet']]:
        request = self.context.get('request', None)
        if not request:
            return None

        query = {self.target_field: request.user.id}
        return super().get_queryset().filter(**query)


class PrescriptionListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display',
                                   help_text='환자의 상태(ex: NONE, NORMAL, ABNORMAL, UNKNOWN 중 한 가지)')

    class Meta:
        model = Prescription
        fields = PrescriptionFields.list_field
        extra_kwargs = {
            'writer': {'help_text': '작성자(의사)의 primary key(ex: 2)',
                       'read_only': True},
            'patient': {'help_text': '환자의 primary key(ex:5)',
                        'read_only': True},
            'checked': {'help_text': '스케줄에 해당하는 환자의 파일을 의사가 모두 확인했을 경우 true, 그렇지 않을 경우 false',
                        'read_only': True},
            'created_at': {'help_text': '소견서 작성일(ex: 2021-01-01T00:00:00)',
                           'read_only': True}
        }


class PrescriptionDetailSerializer(PrescriptionListSerializer):
    class Meta(PrescriptionListSerializer.Meta):
        fields = PrescriptionFields.detail_field
        extra_kwargs = ChainMap(PrescriptionListSerializer.Meta.extra_kwargs,
                                {
                                    'description': {'help_text': '소견서 내용(ex: 환자에게 이상 징후가 발견됨)'},
                                    'updated_at': {'help_text': '소견서 수정 날짜(ex: 2021-01-01T00:00:00)'},
                                    'start_date': {'help_text': '업로드 시작일(ex: 2021-01-01)'},
                                    'end_date': {'help_text': '업로드 종료일(ex:2021-01-05)'}
                                })


class PrescriptionCreateSerializer(PrescriptionSerializerMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:prescription-detail-update',
        lookup_field='pk',
        help_text='detail url'
    )
    writer = serializers.HiddenField(default=CurrentUserDefault(),
                                     help_text='작성자의 primary key(ex:2, hidden field)')
    patient = FilteredPrimaryKeyRelatedField(queryset=Patient.objects.select_all(),
                                             write_only=True, target_field='doctor_id',
                                             help_text='환자의 primary key(ex:5)')
    doctor_files = DoctorFileInPrescriptionSerializer(many=True, read_only=True,
                                                      help_text='의사가 업로드한 파일 정보(읽기 전용)')
    doctor_upload_files = serializers.ListField(child=serializers.FileField(), write_only=True,
                                                help_text='업로드할 파일 정보(리스트 타입, 쓰기 전용)')
    start_date = serializers.DateField(help_text='업로드 시작일(ex: 2021-01-01)')
    end_date = serializers.DateField(help_text='업로드 종료일(ex:2021-01-05)')
    checked = serializers.BooleanField(default=False, read_only=True, help_text='환자가 올린 파일을 의사가 확인했는지 여부(읽기 전용)')

    class Meta(PrescriptionDetailSerializer.Meta):
        fields = ['url'] + PrescriptionDetailSerializer.Meta.fields + ['doctor_files', 'doctor_upload_files']


class FilePrescriptionListSerializer(serializers.ModelSerializer):
    uploaded = serializers.BooleanField(read_only=True, help_text='업로드 여부(ex:True 또는 False')
    status = serializers.CharField(source='get_status_display',
                                   help_text='파일을 통해 의사가 진단한 환자의 상태(ex:NONE, NORMAL, ABNORMAL, UNKNOWN 중 한개')

    class Meta:
        model = FilePrescription
        fields = FilePrescriptionFields.list_field
        extra_kwargs = {
            'prescription': {'help_text': '소견서 객체의 primary key'},
            'checked': {'help_text': '의사가 파일을 확인했는지 여부(ex: True or False)'},
            'date': {'help_text': '업로드 해야할 날짜(ex: 2021-01-01)'},
            'created_at': {'help_text': 'file_prescription 객체 생성일'},
            'updated_at': {'help_text': '객체 수정일'}
        }


class FilePrescriptionDetailSerializer(FilePrescriptionListSerializer):
    class Meta:
        model = FilePrescription
        fields = FilePrescriptionFields.detail_field
        extra_kwargs = ChainMap(FilePrescriptionListSerializer.Meta.extra_kwargs,
                                {
                                    'description': {'help_text': '파일에 대한 소견'},
                                    'day_number': {'help_text': '몇번째 날짜인지 표시'},
                                    'active': {'help_text': '스케줄 활성화 여부'},

                                })


# old version

class FilePrescriptionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:file-prescription-detail-update',
        lookup_field='pk',
        help_text='file-prescription detail url'
    )
    description = serializers.CharField(default='',
                                        help_text='업로드된 파일을 바탕으로 의사가 작성한 소견서 내용(ex: 영상 파일을 확인해보니 우울증이 의심됨)')
    status = serializers.ChoiceField(choices=HealthStatus.choices,
                                     help_text='파일을 통해 의사가 진단한 환자의 상태(ex:NONE, NORMAL, ABNORMAL, UNKNOWN 중 한개')
    created_at = serializers.DateTimeField(read_only=True, help_text='객체 생성일')
    updated_at = serializers.DateTimeField(read_only=True, help_text='객체 수정일')
    deleted = serializers.BooleanField(read_only=True, help_text='일정이 지났거나 관리자에 의해 삭제된 스케줄인지 여부')
    prescription = serializers.PrimaryKeyRelatedField(read_only=True, help_text='소견서 객체의 primary key')
    day_number = serializers.IntegerField(read_only=True, help_text='몇번째 날짜인지 표시')
    date = serializers.DateField(read_only=True, help_text='환자가 파일을 업로드 해야할 날짜')
    active = serializers.BooleanField(read_only=True, default=True, help_text='스케줄 활성화 여부')
    uploaded = serializers.BooleanField(read_only=True, help_text='파일 업로드 여부')
    checked = serializers.BooleanField(help_text='의사가 환자 파일을 확인했는지 여부')

    class Meta:
        model = FilePrescription
        fields = ['url', 'id', 'prescription', 'description', 'status', 'day_number', 'date', 'deleted', 'active',
                  'uploaded', 'checked', 'created_at', 'updated_at']


class FilePrescriptionCreateSerializer(FilePrescriptionSerializer):
    prescription = serializers.PrimaryKeyRelatedField(queryset=Prescription.objects.select_all(),
                                                      help_text='소견서 객체의 primary key')

    # active = serializers.BooleanField(read_only=True)
    # uploaded = serializers.BooleanField(read_only=True)
    # checked = serializers.BooleanField(read_only=True)

    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields


class NestedFilePrescriptionSerializer(FilePrescriptionSerializer):
    patient_files = PatientUploadedFileListSerializer(many=True)  # + PatientSerializer

    class Meta(FilePrescriptionSerializer.Meta):
        fields = FilePrescriptionSerializer.Meta.fields + ['patient_files']


class NestedPrescriptionSerializer(PrescriptionDetailSerializer):
    file_prescriptions = NestedFilePrescriptionSerializer(many=True)

    class Meta(PrescriptionDetailSerializer.Meta):
        fields = PrescriptionDetailSerializer.Meta.fields + ['file_prescriptions']
