from django.urls import include, path
from django.contrib import admin

from filebrowser.sites import site

admin.autodiscover()

urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
]
