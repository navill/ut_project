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
    queryset = DataFile.objects.all().necessary_fields()

    def get_queryset(self):
        user = self.request.user
        # uploader_role = self._get_user_role(user)
        queryset = super().get_queryset().join_prescription_writer()
        if user.is_doctor:
            queryset = queryset.join_uploader('uploader__doctor'). \
                filter_prescription_writer(user). \
                filter_uploader(user)
        elif user.is_patient:
            queryset = queryset.join_uploader('uploader__patient'). \
                filter_uploader(user)

        # queryset = super().get_queryset().join_uploader(uploader_role)
        return queryset if user.is_superuser else queryset

    def _get_user_role(self, user):
        if user.is_doctor:
            query = 'uploader__doctor'
        elif user.is_patient:
            query = 'uploader__patient'
        return query
