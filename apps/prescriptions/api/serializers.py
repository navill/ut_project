from rest_framework import serializers

from accounts.models import Patient
from prescriptions.models import Prescription


# # for browser
# class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
#     def get_queryset(self):
#         """
#         request 유저가 의사일 경우: Patient.objects.filter(user_doctor=request.user.doctor)
#         -> 의사가 담당하는 환자 리스트
#         request 유저가 사용자(환자)일 경우: Patient.objects.filter(user=request.user)
#         -> 사용자(환자) 자신
#         """
#         request_user = self.context.get('request', None).user
#         queryset = super(UserFilteredPrimaryKeyRelatedField, self).get_queryset()
#         query = {}
#         if request_user.is_doctor:
#             query = {'user_doctor': request_user.doctor}
#         elif request_user.is_patient:
#             query = {'user': request_user}
#         return queryset.filter(**query)


class PrescriptionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='prescriptions:detail-update',
        lookup_field='pk'
    )
    writer = serializers.PrimaryKeyRelatedField(read_only=True)
    user_patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    # user_patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    description = serializers.CharField()
    created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = Prescription
        fields = ['url', 'writer', 'user_patient', 'description', 'created', 'updated']
