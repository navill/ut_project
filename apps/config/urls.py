import debug_toolbar
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from accounts.api.views import AccountsTokenPairView, TokenLogoutView, AccountsTokenRefreshView
from config.utils.doc_utils import schema_view

urlpatterns = [
    path('core-api/', include('core.api.urls', namespace='core-api')),

    path('accounts/', include('accounts.api.urls', namespace='accounts')),
    path('prescriptions/', include('prescriptions.api.urls', namespace='prescriptions')),
    path('hospitals/', include('hospitals.api.urls', namespace='hospitals')),
    path('datafiles/', include('files.api.urls', namespace='files')),

    path('token', AccountsTokenPairView.as_view(), name='token-login'),
    path('token/refresh', AccountsTokenRefreshView.as_view(), name='token-refresh'),
    path('token/logout', TokenLogoutView.as_view(), name='token-logout'),
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
]

urlpatterns += [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
