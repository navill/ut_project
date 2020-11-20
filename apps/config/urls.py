import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),

]
if settings.DEBUG:
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
