from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Create your models here.
class CeleryTestModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    result = models.CharField(max_length=100, null=True, blank=True)
    host = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
