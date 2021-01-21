class QuerySetMixin:
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_doctor:
            queryset = queryset.select_doctor().select_prescription(). \
                filter_prescription_writer(user)
        elif user.is_patient:
            print(1)
            queryset = queryset.select_patient().select_file_prescription().filter_uploader(user)
            print(2)
        return queryset if user.is_superuser else queryset

    # def _get_user_role(self, user):
    #     if user.is_doctor:
    #         query = 'uploader__doctor'
    #     elif user.is_patient:
    #         query = 'uploader__patient'
    #     return query
