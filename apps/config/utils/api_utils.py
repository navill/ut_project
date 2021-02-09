from typing import Tuple

from rest_framework.response import Response


class InputValueSupporter:
    fields_to_display: Tuple[str] = ()

    def get(self, request):
        default_values = None

        if self.fields_to_display is None:
            raise Exception(f"{self.__class__.__name__} should include a 'fields_to_display' attribute")

        if request.GET.get('default', None) == 'true':
            default_values = self.get_default_input_values(fields_to_display=self.fields_to_display)

        return Response(default_values)

    def get_default_input_values(self, fields_to_display: Tuple[str]):
        fields = self.get_serializer().fields
        default_values = {}

        for field_name in fields_to_display:
            if not hasattr(fields[field_name], 'choices'):
                raise AttributeError(f"'{field_name}' field is not choices field")
            choices = ({field_id: field_value} for field_id, field_value in fields[field_name].choices.items())
            default_values[field_name] = choices

        return default_values
