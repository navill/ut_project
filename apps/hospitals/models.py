from django.db import models
from django.urls import reverse


class MedicalCenterQuerySet(models.QuerySet):
    pass


class MedicalCenterManager(models.Manager):
    def get_queryset(self) -> MedicalCenterQuerySet:
        return MedicalCenterQuerySet(self.model, using=self._db)

    def prefetch_all(self) -> MedicalCenterQuerySet:
        return self.get_queryset().prefetch_related('department__major')


class MedicalCenter(models.Model):
    country = models.CharField(max_length=25, default='한국')
    city = models.CharField(max_length=20, default='서울특별시')
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    main_call = models.CharField(max_length=20)
    sub_call = models.CharField(max_length=20)

    objects = MedicalCenterManager()

    def __str__(self) -> str:
        return str(self.name)

    def get_absoulte_url(self) -> str:
        return reverse('hospitals:hospital-retrieve', kwargs={'pk': self.pk})


class DepartmentQuerySet(models.QuerySet):
    pass


class DepartmentManager(models.Manager):
    def get_queryset(self) -> DepartmentQuerySet:
        return DepartmentQuerySet(self.model, using=self._db)

    def select_all(self) -> DepartmentQuerySet:
        return self.get_queryset().select_related('medical_center')

    def prefetch_all(self) -> DepartmentQuerySet:
        return self.get_queryset().prefetch_related('major')


class Department(models.Model):
    medical_center = models.ForeignKey(MedicalCenter, on_delete=models.CASCADE, related_name='department')
    name = models.CharField(max_length=120, default='정신의학과')
    call = models.CharField(max_length=20, default='')

    objects = DepartmentManager()

    def __str__(self) -> str:
        return f'{self.medical_center}-{self.name}'

    def get_absoulte_url(self) -> str:
        return reverse('hospitals:department-retrieve', kwargs={'pk': self.pk})


class MajorQuerySet(models.QuerySet):
    def select_all(self) -> 'MajorQuerySet':
        return self.select_related('department__medical_center')

    def prefetch_all(self) -> 'MajorQuerySet':
        return self.prefetch_related('doctor_major')


class MajorManager(models.Manager):
    def get_queryset(self) -> MajorQuerySet:
        return MajorQuerySet(self.model, using=self._db).order_by('id')
        # .prefetch_related(Prefetch('department__medical_center', queryset=MedicalCenter.objects.all()))

    def select_all(self) -> MajorQuerySet:
        return self.get_queryset().select_all()

    def prefetch_all(self) -> MajorQuerySet:
        return self.get_queryset().prefetch_all()

    def related_all(self) -> MajorQuerySet:
        return self.get_queryset().select_all().prefetch_all()


class Major(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='major')
    name = models.CharField(max_length=20, default='정신의학')
    call = models.CharField(max_length=20)

    objects = MajorManager()

    def __str__(self) -> str:
        return f'{self.department}-{self.name}'

    def get_absoulte_url(self) -> str:
        return reverse('hospitals:major-retrieve', kwargs={'pk': self.pk})
