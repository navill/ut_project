from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_path_parameters(self, path, view_cls):
        parameters = super().get_path_parameters(path, view_cls)
        for p in parameters:
            if p.in_ == openapi.IN_PATH and p.type == openapi.TYPE_STRING:
                p.type = getattr(view_cls, f'path_type_{p.name}', openapi.TYPE_STRING)
        return parameters
