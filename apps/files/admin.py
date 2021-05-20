import contextlib
import io
import zipfile

from django.contrib import admin
# Register your models here.
from django.http import HttpResponse

from files.temp_models import TempHospitalFiles


@contextlib.contextmanager
def get_memory_container():
    in_memory = io.BytesIO()
    try:
        yield in_memory
    finally:
        in_memory.close()


def download_files(modeladmin, request, queryset):  # todo: refactoring
    # in_memory = io.BytesIO()
    with get_memory_container() as in_memory:
        with zipfile.ZipFile(in_memory, 'w', zipfile.ZIP_DEFLATED, False) as zip_file:
            for number, query in enumerate(queryset):
                with open(query.file.path, 'rb') as query_file:
                    data = io.BytesIO(query_file.read())
                    zip_file.writestr(query.file.name, data.getvalue())

        in_memory.seek(0)

        response = HttpResponse(in_memory, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="compressed_health_file.zip"'
        return response


download_files.short_description = "Download checked files"


class TempHospitalFilesAdmin(admin.ModelAdmin):
    fields = ['doctor', 'file', 'file_name', 'file_info', 'extension', 'file_type', 'created_at', 'updated_at']
    list_display = ['doctor', 'file_name', 'extension', 'file_type', 'created_at']
    list_filter = ['doctor', 'extension', 'file_type']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    list_display_links = ['file_name']
    actions = [download_files]


admin.site.register(TempHospitalFiles, TempHospitalFilesAdmin)
