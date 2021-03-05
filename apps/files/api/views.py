from typing import Type

from django.db.models import QuerySet
from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import FileUploadParser, MultiPartParser

from accounts.api.permissions import IsDoctor, IsPatient, IsOwner, CareDoctorReadOnly
from config.utils.api_utils import InputValueSupporter
from files.api.mixins import QuerySetMixin
from files.api.serializers import (PatientFileUploadSerializer,
                                   DoctorFileUploadSerializer,
                                   DoctorFileListSerializer,
                                   PatientFileListSerializer,
                                   PatientUploadedFileListSerializer,
                                   DoctorUploadedFileListSerializer,
                                   DoctorFlieRetrieveSerializer,
                                   DoctorUploadedFileRetrieveSerializer,
                                   PatientFlieRetrieveSerializer,
                                   DoctorFileDownloadSerializer,
                                   PatientFileDownloadSerializer)
from files.api.utils import Downloader
from files.models import DoctorFile, PatientFile


class DoctorFileListAPIView(QuerySetMixin, ListAPIView):
    """
    [LIST] 의사가 올린 파일 리스트

    ---
    - 기능: 의사가 업로드한 파일의 리스트 출력
    - 권한: IsDoctor

    """
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileListSerializer


class DoctorFileRetrieveAPIView(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE] 의사가 올린 파일 세부 정보

    ---
    - 기능: 의사가 업로드한 파일의 세부 정보 출력
    - 권한: IsOwner

    """
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsOwner]
    serializer_class = DoctorFlieRetrieveSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return super(DoctorFileRetrieveAPIView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file': openapi.Schema(type=openapi.TYPE_STRING,
                                   description='파일 정보(파일 디렉토리)'), }
    ),
        responses={200: DoctorFlieRetrieveSerializer, 400: 'Bad Request'})
    def put(self, request, *args, **kwargs):
        return super(DoctorFileRetrieveAPIView, self).put(request, *args, **kwargs)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file': openapi.Schema(type=openapi.TYPE_STRING,
                                   description='파일 정보(파일 디렉토리)'), }
    ),
        responses={200: DoctorFlieRetrieveSerializer, 400: 'Bad Request'})
    def patch(self, request, *args, **kwargs):
        return super(DoctorFileRetrieveAPIView, self).patch(request, *args, **kwargs)


class DoctorFileUploadAPIView(CreateAPIView):
    """
    [CREATE] 파일 업로드(의사용)

    ---
    - 기능: 의사가 파일을 업로드할 때 사용
    - 권한: IsDoctor
    """
    queryset = DoctorFile.objects.select_all()
    permission_classes = [IsDoctor]
    serializer_class = DoctorFileUploadSerializer
    # parser_classes = (FileUploadParser,)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'prescription': openapi.Schema(type=openapi.TYPE_INTEGER,
                                           description='소견서 객체 pk'),
            'file': openapi.Schema(type=openapi.TYPE_STRING,
                                   description='파일 정보(파일 디렉토리)'), }
    ),
        responses={201: DoctorFileUploadSerializer, 400: 'Bad Request'})
    def post(self, request, *args, **kwargs):
        return super(DoctorFileUploadAPIView, self).post(request, *args, **kwargs)


# class DoctorUploadedFileListAPIView(ListAPIView):
#     """
#     [LIST] 의사가 업로드한 파일의 리스트
#
#     """
#     queryset = DoctorFile.objects.select_all()
#     permission_classes = [IsDoctor]
#     serializer_class = DoctorUploadedFileListSerializer
#
#     def get_queryset(self) -> Type[QuerySet]:
#         user = self.request.user
#         queryset = super().get_queryset()
#         queryset = queryset.filter_patient(user.id)
#         return queryset


# class DoctorUploadedFileUpdateAPIView(RetrieveUpdateAPIView):
#     queryset = DoctorFile.objects.select_all()
#     permission_classes = [IsDoctor]
#     serializer_class = DoctorUploadedFileRetrieveSerializer
#     parser_classes = (FileUploadParser,)
#     lookup_field = 'id'
#
#     def get_queryset(self) -> Type[QuerySet]:
#         user = self.request.user
#         queryset = super().get_queryset()
#         queryset = queryset.filter_patient(user.id)
#         return queryset
#
#     @swagger_auto_schema(operation_description='Upload file...', )
#     def put(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)


class PatientFileListAPIView(QuerySetMixin, ListAPIView):
    """
    [LIST] 환자가 업로드한 파일의 리스트

    ---
    - 기능: 환자가 올린 파일의 리스트를 출력
    - 권한: IsPatient

    """
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFileListSerializer


class PatientFileRetrieveAPIView(RetrieveUpdateAPIView):
    """
    [DETAIL, UPDATE] 환자가 올린 파일의 세부 정보 및 수정

    ---
    - 기능: 환자가 올린 파일의 세부 정보(detail) 표시 및 정보 수정
    - 권한: IsOwner(읽기 & 쓰기), IsDoctor(읽기)

    """
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsOwner | IsDoctor]
    serializer_class = PatientFlieRetrieveSerializer
    parser_classes = (FileUploadParser,)
    lookup_field = 'id'


class PatientFileUploadAPIView(CreateAPIView):
    """
    [CREATE] 파일 업로드(환자용)

    ---
    - 기능: 환자용 파일 업로드
    - 권한: IsPatient
    """
    queryset = PatientFile.objects.select_all()
    permission_classes = [IsPatient]
    serializer_class = PatientFileUploadSerializer

    # parser_classes = (MultiPartParser,)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file_prescription': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                description='FilePrescription pk'),
            'file': openapi.Schema(type=openapi.TYPE_STRING,
                                   description='파일 정보(로컬 파일 디렉토리)'), }
    ),
        responses={201: PatientFileUploadSerializer, 400: 'Bad Request'})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# class PatientUploadedFileListAPIView(ListAPIView):
#     queryset = PatientFile.objects.select_all()
#     permission_classes = [IsPatient]
#     serializer_class = PatientUploadedFileListSerializer
#     lookup_field = 'id'
#
#     def get_queryset(self) -> Type[QuerySet]:
#         user = self.request.user
#         return super().get_queryset().filter_uploader(uploader_id=user.id).filter_unchecked_list()


class DoctorFileDownloadAPIView(RetrieveAPIView):
    """
    [DETAIL] 의사 파일 다운로드

    ---
    - 기능: 의사가 파일 다운로드 링크 표시
    - 권한: IsOwner

    """
    queryset = DoctorFile.objects.all()
    permission_classes = [IsOwner]
    serializer_class = DoctorFileDownloadSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()


class PatientFileDownloadAPIView(RetrieveAPIView):
    """
    [DETAIL] 환자 파일 다운로드

    ---
    - 기능: 환자 또는 의사가 환자의 파일을 다운로드 할 수 있도로 링크 표시
    - 권한: IsOwner(환자), CareDoctorReadOnly(담당 의사)

    """
    queryset = PatientFile.objects.all()
    permission_classes = [IsOwner | CareDoctorReadOnly]
    serializer_class = PatientFileDownloadSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs) -> 'FileResponse':
        file_object = self.get_object()
        downloader = Downloader(instance=file_object)
        return downloader.response()
