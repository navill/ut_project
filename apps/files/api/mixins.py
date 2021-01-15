from files.models import DataFile


# class CurrentUserRelatedFieldMixin:
#     def filter_current_user_by(self, attribute_name):
#         request = self.context.get('request', None)
#         queryset = super().get_queryset()
#         if not request or not queryset:
#             return None
#         query = {attribute_name: request.user}
#         return queryset.filter(**query)


class QuerySetMixin:
    queryset = DataFile.objects.select_all().necessary_fields()

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_doctor:
            queryset = queryset.select_doctor().select_prescription(). \
                filter_prescription_writer(user).filter_checked_list()
        elif user.is_patient:
            queryset = queryset.select_patient().select_doctor().filter_uploader(user)

        return queryset if user.is_superuser else queryset

    def _get_user_role(self, user):
        if user.is_doctor:
            query = 'uploader__doctor'
        elif user.is_patient:
            query = 'uploader__patient'
        return query
