from drf_yasg import openapi

to_display_choices = openapi.Parameter('default', openapi.IN_QUERY, description="choices 속성에 대한 출력 여부",
                                       type=openapi.TYPE_BOOLEAN)

# [Deprecated]
# class InputValueSupporter:
#     fields_to_display: Tuple[str] = ()
#
#     @swagger_auto_schema(manual_parameters=[to_display_choices])
#     def get(self, request):
#         """
#         객체 생성(POST) url에서 GET method를 통해 fields_to_display에 등록된 속성(choices)에 대한 항목들 출력
#         ---
#         # 예시(아래 내용은 현재 endpoint와 관계 없음)
#             - PrescriptionCreate.fields_to_display = 'patient', 'status'
#             - url: http://127.0.0.1:8000/core-api/doctors/prescriptions/create?default=true
#
#             - response
#             {
#                 "patient": [
#                     {
#                         "7": "이름: 환자 삼, 나이: 33, 성별: 남"
#                     },
#                     {
#                         "8": "이름: 환자 사, 나이: 33, 성별: 남"
#                     }
#                 ],
#                 "status": [
#                     {
#                         "NONE": "없음"
#                     },
#                     {
#                         "NORMAL": "정상"
#                     },
#                     {
#                         "ABNORMAL": "비정상"
#                     },
#                     {
#                         "UNKNOWN": "알 수 없음"
#                     }
#                 ]
#             }
#
#         """
#         default_values = None
#         if self.fields_to_display is None:
#             raise Exception(f"{self.__class__.__name__} should include a 'fields_to_display' attribute")
#
#         if request.GET.get('default', None) == 'true':
#             default_values = self.get_default_input_values(fields_to_display=self.fields_to_display)
#
#         return Response(default_values)
#
#     def get_default_input_values(self, fields_to_display: Tuple[str]):
#         fields = self.get_serializer().fields
#         default_values = {}
#
#         for field_name in fields_to_display:
#             if not hasattr(fields[field_name], 'choices'):
#                 raise AttributeError(f"'{field_name}' field is not choices field")
#             choices = ({field_id: field_value} for field_id, field_value in fields[field_name].choices.items())
#             default_values[field_name] = choices
#
#         return default_values
