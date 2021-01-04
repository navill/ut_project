class CurrentUserRelatedFieldMixin:
    def filter_current_user_by(self, attribute_name):
        request = self.context.get('request', None)
        queryset = super().get_queryset()
        if not request or not queryset:
            return None
        query = {attribute_name: request.user}
        return queryset.filter(**query)
