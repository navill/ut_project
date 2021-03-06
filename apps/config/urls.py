import debug_toolbar
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from accounts.api.views import AccountsTokenPairView, TokenLogoutView, AccountsTokenRefreshView, session_logout_view
from config.utils.doc_utils import schema_view
from files.api.views import TempFiles, TempFilesUpload, TempFilesDownload, TempFilesBulkDownload

urlpatterns = [
    path('core-api/', include('core.api.urls', namespace='core-api')),

    path('accounts/', include('accounts.api.urls', namespace='accounts')),
    path('prescriptions/', include('prescriptions.api.urls', namespace='prescriptions')),
    path('hospitals/', include('hospitals.api.urls', namespace='hospitals')),
    path('datafiles/', include('files.api.urls', namespace='files')),

    path('token', AccountsTokenPairView.as_view(), name='token-login'),
    path('token/refresh', AccountsTokenRefreshView.as_view(), name='token-refresh'),
    path('token/logout', TokenLogoutView.as_view(), name='token-logout'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-auth/logout', session_logout_view, name='session_logout'),
    path('ut-admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
]

urlpatterns += [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += [
    path('chosun/files', TempFiles.as_view(), name='temp-files'),
    path('chosun/files/upload', TempFilesUpload.as_view(), name='temp-files-upload'),
    path('chosun/files/<int:pk>/download', TempFilesDownload.as_view(), name='temp-files-download'),
    path('chosun/files/download', TempFilesBulkDownload.as_view(), name='temp-files-upload')
]

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
