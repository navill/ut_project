from rest_framework import serializers

from hospitals.models import MedicalCenter, Department, Major


class MedicalCenterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:medicalcenter-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = MedicalCenter
        fields = '__all__'


class MedicalCenterRetrieveSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:medicalcenter-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = MedicalCenter
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:department-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Department
        fields = ['url', 'medical_center', 'name', 'call']


class DepartmentRetreiveSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:department-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Department
        fields = ['url', 'medical_center', 'name', 'call']


class MajorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:major-retrieve',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = Major
        fields = ['url', 'department', 'name', 'call']


class MajorRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ['url', 'department', 'name', 'call']


class DepartmentNestedMajor(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='hospitals:department-retrieve',
        lookup_field='pk',
        read_only=True
    )
    major = MajorSerializer(many=True)

    class Meta:
        model = Department
        fields = ['url', 'medical_center', 'name', 'call', 'major']


class MedicalCenterNestedDepartmentMajor(serializers.ModelSerializer):
    department = DepartmentNestedMajor(many=True)

    class Meta:
        model = MedicalCenter
        fields = ['country', 'city', 'name', 'address', 'postal_code', 'main_call', 'sub_call', 'department']
