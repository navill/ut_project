from typing import Tuple

from rest_framework.response import Response


class InputValueSupporter:
    fields_to_display: Tuple[str] = None

    def get(self, request):
        default_values = None
        if request.GET.get('default', None) == 'true':
            default_values = self.get_default_input_values(field_names=self.fields_to_display)
        return Response(default_values)

    def get_default_input_values(self, field_names: Tuple[str]):
        fields = self.get_serializer().fields
        default_values = {}
        for field_name in field_names:
            choices_list = ({field_id: field_value} for field_id, field_value in fields[field_name].choices.items())
            default_values[field_name] = choices_list

        return default_values
