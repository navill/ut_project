import mimetypes
import os

from django.http import FileResponse


class Downloader:
    def __init__(self, instance):
        self.file_field = instance.file

    def response(self) -> FileResponse:
        filename = self.get_filename(self.file_field)
        content_type, encoding = mimetypes.guess_type(filename)
        return FileResponse(self.file_field.open(), content_type=content_type, as_attachment=True)

    def get_filename(self, file_field):
        filename = os.path.basename(file_field.name)
        return filename
