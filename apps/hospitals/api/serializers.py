from rest_framework import serializers

from hospitals.models import MedicalCenter, Department, Major


class DefaultMedicalCenterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:medicalcenter-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = MedicalCenter
        fields = ['url', 'country', 'city', 'name', 'address', 'postal_code', 'main_call', 'sub_call']


class MedicalCenterSerializer(DefaultMedicalCenterSerializer):
    class Meta(DefaultMedicalCenterSerializer):
        fields = DefaultMedicalCenterSerializer.Meta.fields


class MedicalCenterRetrieveSerializer(DefaultMedicalCenterSerializer):
    pass


class DefaultDepartmentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:department-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Department
        fields = ['url', 'medical_center', 'name', 'call']


class DepartmentSerializer(DefaultDepartmentSerializer):
    pass


class DepartmentRetreiveSerializer(DefaultDepartmentSerializer):
    pass


class DefaultMajorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:major-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Major
        fields = ['url', 'name']


class MajorSerializer(DefaultMajorSerializer):
    class Meta(DefaultMajorSerializer.Meta):
        fields = DefaultMajorSerializer.Meta.fields + ['department', 'call']


class MajorRetrieveSerializer(MajorSerializer):
    pass


class DepartmentNestedMajor(DefaultDepartmentSerializer):
    major = MajorSerializer(many=True)

    class Meta(DefaultDepartmentSerializer.Meta):
        fields = DefaultDepartmentSerializer.Meta.fields + ['major']


class MedicalCenterNestedDepartmentMajor(DefaultMedicalCenterSerializer):
    department = DepartmentNestedMajor(many=True)

    class Meta(DefaultMedicalCenterSerializer.Meta):
        fields = DefaultMedicalCenterSerializer.Meta.fields + ['department']
