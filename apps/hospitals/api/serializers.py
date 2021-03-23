from rest_framework import serializers
from rest_framework.serializers import Serializer

from hospitals.models import MedicalCenter, Department, Major

"""
Medical center serializers
"""


class DefaultMedicalCenterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:medicalcenter-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = MedicalCenter
        fields = ['url', 'id', 'country', 'city', 'name', 'address', 'postal_code', 'main_call', 'sub_call']


class MedicalCenterSerializer(DefaultMedicalCenterSerializer):
    pass


class MedicalCenterCreateSerializer(DefaultMedicalCenterSerializer):
    pass


class MedicalCenterListSerializer(DefaultMedicalCenterSerializer):
    pass


class MedicalCenterRetrieveSerializer(DefaultMedicalCenterSerializer):
    pass


"""
Department serializers
"""


class RawDepartmentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:department-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Department
        fields = ['url', 'id', 'name', 'call']


class DefaultDepartmentSerializer(RawDepartmentSerializer):
    medical_center = MedicalCenterSerializer(read_only=True)

    class Meta(RawDepartmentSerializer.Meta):
        fields = RawDepartmentSerializer.Meta.fields + ['medical_center']


class DepartmentSerializer(DefaultDepartmentSerializer):
    pass


class DepartmentListSerializer(RawDepartmentSerializer):
    class Meta(RawDepartmentSerializer.Meta):
        fields = RawDepartmentSerializer.Meta.fields


class DepartmentCreateSerializer(DefaultDepartmentSerializer):
    medical_center = serializers.PrimaryKeyRelatedField(queryset=MedicalCenter.objects.all())


class DepartmentRetreiveSerializer(DepartmentSerializer):
    pass


"""
Major serializers
"""


class RawMajorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:major-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Major
        fields = ['url', 'id', 'name', 'call']


class DefaultMajorSerializer(RawMajorSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.select_related())

    class Meta(RawMajorSerializer.Meta):
        fields = RawMajorSerializer.Meta.fields + ['department']


class MajorSerializer(DefaultMajorSerializer):
    department = RawDepartmentSerializer(read_only=True)


class MajorListSerializer(RawMajorSerializer):
    class Meta(RawMajorSerializer.Meta):
        fields = RawMajorSerializer.Meta.fields


class MajorCreateSerializer(MajorSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.select_related('medical_center'))


class MajorRetrieveSerializer(MajorSerializer):
    pass


"""
Nested serializer
"""


class DepartmentNestedMajor(RawDepartmentSerializer):
    major = RawMajorSerializer(many=True)

    class Meta(RawDepartmentSerializer.Meta):
        fields = RawDepartmentSerializer.Meta.fields + ['major']


class MedicalCenterNestedDepartmentMajor(MedicalCenterSerializer):
    department = DepartmentNestedMajor(many=True)

    class Meta(DefaultMedicalCenterSerializer.Meta):
        fields = ['id', 'city', 'name'] + ['department']


"""
Choice Serializer
"""


class MedicalCenterChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCenter
        fields = ['id', 'name']


class DepartmentChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class MajorChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ['id', 'name']
