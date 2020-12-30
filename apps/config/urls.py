import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from accounts.api.views import AccountsTokenPairView, TokenLogoutView, AccountsTokenRefreshView

urlpatterns = [

    path('accounts/', include('accounts.api.urls', namespace='accounts')),
    path('prescriptions/', include('prescriptions.api.urls', namespace='prescriptions')),
    path('hospitals/', include('hospitals.api.urls', namespace='hospitals')),
    path('datafiles/', include('files.api.urls', namespace='files')),
    path('admin/', admin.site.urls),

    path('token', AccountsTokenPairView.as_view(), name='token-login'),
    path('token/refresh', AccountsTokenRefreshView.as_view(), name='token-refresh'),
    path('token/logout', TokenLogoutView.as_view(), name='token-logout'),

    path('', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
