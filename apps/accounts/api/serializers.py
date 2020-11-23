from rest_framework import serializers

from accounts.models import BaseUser


class StaffSignUpSerializer(serializers.ModelSerializer):
    department = serializers.CharField(max_length=100)

    class Meta:
        model = BaseUser
        fields = ['username', 'password', 'department']


class NormalSignUpSerializer(serializers.ModelSerializer):
    description = serializers.CharField(max_length=100)

    class Meta:
        model = BaseUser
        fields = ['username', 'password', 'description']
