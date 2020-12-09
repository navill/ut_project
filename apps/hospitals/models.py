from django.db import models

MAJOR = (('PSYCHIATRIST', 'psychiatrist'),
         ('PSYCHIATRIST', 'psychiatrist'),
         ('PSYCHIATRIST', 'psychiatrist'))

COUNTRY = (
    ('KOREA', '한국'),
    ('USA', '미국'),
)

CITY = (
    ('SEOUL', '서울'),
    ('GWANGJU', '광주')
)


class Hospital(models.Model):
    country = models.CharField(max_length=25, choices=COUNTRY, default='KOREA')
    city = models.CharField(max_length=20, choices=CITY, default='GWANGJU')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    main_call = models.CharField(max_length=20)
    sub_call = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class MajorQuerySet(models.QuerySet):
    pass


class MajorManager(models.Manager):
    def get_queryset(self):
        return MajorQuerySet(self.model, using=self._db).select_related('hospital')


class Major(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='major')
    name = models.CharField(max_length=20, choices=MAJOR, default='PSYCHIATRIST')
    main_call = models.CharField(max_length=20)
    sub_call = models.CharField(max_length=20)

    objects = MajorManager()

    def __str__(self):
        return self.name
