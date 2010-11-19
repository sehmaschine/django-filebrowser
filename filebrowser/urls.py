from django.conf.urls.defaults import *

from filebrowser.settings import *

urlpatterns = patterns('',
    # filebrowser urls
    url(r'^browse/$', 'filebrowser.views.browse', name="fb_browse"),
    url(r'^mkdir/', 'filebrowser.views.mkdir', name="fb_mkdir"),
    url(r'^rename/$', 'filebrowser.views.rename', name="fb_rename"),
    url(r'^delete/$', 'filebrowser.views.delete', name="fb_delete"),
    url(r'^versions/$', 'filebrowser.views.versions', name="fb_versions"),
    (r'^', include('filebrowser.upload_frontends.%s.urls' % UPLOAD_FRONTEND)),
)

