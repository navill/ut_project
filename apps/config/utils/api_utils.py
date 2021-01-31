from typing import Tuple

from rest_framework import serializers
from rest_framework.response import Response


class InputValueSupporter:
    fields_to_display: Tuple[str] = None

    def get(self, request):
        if self.fields_to_display is None:
            raise Exception(f"{self.__class__.__name__} should include a 'fields_to_display' attribute")

        default_values = None
        if request.GET.get('default', None) == 'true':
            default_values = self.get_default_input_values(fields_to_display=self.fields_to_display)
        return Response(default_values)

    def get_default_input_values(self, fields_to_display: Tuple[str]):
        fields = self.get_serializer().fields
        default_values = {}
        for field in fields_to_display:
            if not hasattr(fields[field], 'choices'):
                raise AttributeError(f"'{field}' field is not choices field")
            choices_list = ({field_id: field_value} for field_id, field_value in fields[field].choices.items())
            default_values[field] = choices_list

        return default_values
