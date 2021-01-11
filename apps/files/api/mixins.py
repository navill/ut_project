class CurrentUserRelatedFieldMixin:
    def filter_current_user_by(self, attribute_name):
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        query = {attribute_name: request.user}
        return queryset.filter(**query)


class QuerySetMixin:
    def get_queryset(self):
        user = self.request.user
        query_name = None
        if user.is_doctor:
            query_name = 'uploader__doctor'
        elif user.is_patient:
            query_name = 'uploader__patient'
        queryset = super().get_queryset()

        # def filter_current_user(self, current_user):
        #     return self.filter(uploader_id=current_user.id)
        #
        # def filter_current_user_for_prescription(self, current_user):
        #     return self.filter(prescription__user=current_user.id)
        #
        # def related_uploader(self, query_word: str):
        #     return self.select_related(query_word)

        return queryset.filter_current_user(user). \
            filter_current_user_for_prescription(user). \
            join_uploader_as_role(query_name)
