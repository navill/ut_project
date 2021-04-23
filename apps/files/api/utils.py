import datetime
import mimetypes
import os
from typing import Union, TYPE_CHECKING, NoReturn

from django.db.models import F
from django.db.models.functions import Concat
from django.http import FileResponse

if TYPE_CHECKING:
    from files.models import DoctorFile, PatientFile
    from django.db.models.fields.files import FieldFile


class Downloader:
    def __init__(self, instance: Union['DoctorFile', 'PatientFile']):
        self.field_file: 'FieldFile' = instance.file

    def response(self) -> FileResponse:
        filename = self._get_filename(self.field_file)
        content_type, encoding = mimetypes.guess_type(filename)
        # FileResponse._wrap_file_to_stream_close() 메서드가 context manager 처럼 동작하므로 self.file_field.close() 필요 없음
        return FileResponse(self.field_file.open(), content_type=content_type, as_attachment=True)

    def _get_filename(self, field_file: 'FieldFile'):
        filename = os.path.basename(field_file.name)
        return filename


def delete_file(path: str) -> NoReturn:
    if os.path.isfile(path):
        os.remove(path)


def directory_path(instance: Union['DoctorFile', 'PatientFile'], filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    splited_name = filename.split('.')
    filename = splited_name[:-1]
    extension = splited_name[-1]
    return f'{day}/{extension}/{instance.uploader}_{time}_{filename}.{extension}'


def concatenate_name(target_field: str) -> Concat:
    full_name = Concat(F(f'{target_field}__last_name'), F(f'{target_field}__first_name'))
    return full_name
