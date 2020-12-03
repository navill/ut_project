from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from accounts.mixins.form_mixins import CommonUserQuerySetMixin


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
    address = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=14, default='')

    objects = BaseManager()


class StaffQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class StaffManager(models.Manager):
    def get_queryset(self):
        return StaffQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_staff_user = super().all().active()
        return active_staff_user


class StaffUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=255, default='')
    type = models.CharField(max_length=10, default='staff')

    objects = StaffManager()

    def get_absolute_url(self):
        return reverse('accounts:staff:detail', kwargs={'pk': self.pk})

    @property
    def is_staff(self):
        return True


class NormalQuerySet(CommonUserQuerySetMixin, models.QuerySet):
    pass


class NormalManager(models.Manager):
    def get_queryset(self):
        return NormalQuerySet(self.model, using=self._db).select_related('user')

    def all(self):
        active_normal_user = super().all().active()
        return active_normal_user


class NormalUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True)
    description = models.TextField(default='')
    type = models.CharField(max_length=10, default='normal')

    objects = NormalManager()

    def get_absolute_url(self):
        return reverse('accounts:normal:detail', kwargs={'pk': self.pk})

    @property
    def is_normal(self):
        return True
