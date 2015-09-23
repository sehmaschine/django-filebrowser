from django.conf.urls import include, url
from django.contrib import admin

from filebrowser.sites import site

admin.autodiscover()

urlpatterns = [
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
