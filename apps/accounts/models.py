from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from accounts.mixins import CommonUserQuerySetMixin


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class BaseManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(username=username)

    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)

    def all(self):
        return super().all().active().order_by('-date_joined')


class BaseUser(AbstractUser):
    is_staff = models.BooleanField(default=False)
    is_normal = models.BooleanField(default=False)

    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, default='')

    objects = BaseManager()


class StaffQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class StaffManager(models.Manager):
    def get_queryset(self):
        return StaffQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_staff_user = super().all().active().staff()
        return active_staff_user


class StaffUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=255, default='')

    objects = StaffManager()

    def get_absolute_url(self):
        return reverse('accounts:staff:detail', kwargs={'pk': self.pk})


class NormalQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class NormalManager(models.Manager):
    def get_queryset(self):
        return NormalQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_normal_user = super().all().active().normal()
        return active_normal_user


class NormalUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    description = models.TextField(default='')

    objects = NormalManager()

    def get_absolute_url(self):
        return reverse('accounts:normal:detail', kwargs={'pk': self.pk})
