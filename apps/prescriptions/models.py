from django.db import models

from accounts.models import Patient, BaseUser


class PrescriptionManager(models.Manager):
    def all(self):
        return self.get_queryset().order_by('-created')


class Prescription(models.Model):
    # 'writer 필요 없을듯'
    writer = models.ForeignKey(BaseUser, on_delete=models.SET_NULL, null=True, related_name='prescription_by')
    user_patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, related_name='prescription_to')
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    objects = PrescriptionManager()
#
# def pre_save_slug(sender, instance, *args, **kwargs):
#     if not instance.slug:
#         instance.slug = create_slug(sender, instance)
#
#
# pre_save.connect(pre_save_slug, sender=Prescription)
#
#
# def create_slug(klass, instance, new_slug=None):
#     now_day = date.today().strftime("%Y-%m-%d")
#     slug = slugify(f'{now_day}-{instance.writer.get_full_name()}', allow_unicode=True)
#
#     if new_slug is not None:
#         slug = new_slug
#     queryset = klass.objects.filter(slug=slug).order_by("-id")
#     if queryset.exists():
#         new_slug = f'{slug}-{queryset.first().id}'
#         return create_slug(klass, instance, new_slug=new_slug)
#     return slug
