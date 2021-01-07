import mimetypes
import os

from django.http import FileResponse


class Downloader:
    def __init__(self, instance):
        self.file_field = instance.file

    def response(self) -> FileResponse:
        filename = self._get_filename(self.file_field)
        content_type, encoding = mimetypes.guess_type(filename)
        # FileResponse._wrap_file_to_stream_close() 메서드가 context manager 처럼 동작하므로 self.file_field.close() 필요 없음
        return FileResponse(self.file_field.open(), content_type=content_type, as_attachment=True)

    def _get_filename(self, file_field):
        filename = os.path.basename(file_field.name)
        return filename
