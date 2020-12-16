from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from hospitals.models import Hospital


class HospitalListCreateView(ListCreateAPIView):
    queryset = Hospital.objects.all()
    serializer_class = None
    permission_classes = [AllowAny]


class HospitalRetrieveUpdate():
    pass
