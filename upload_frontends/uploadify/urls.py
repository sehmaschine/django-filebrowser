from django.conf.urls.defaults import *

from filebrowser.settings import *

urlpatterns = patterns('',    
    url(r'^upload/', 'filebrowser.upload_frontends.%s.views.upload' % UPLOAD_FRONTEND, name="fb_upload"),
    url(r'^check_file/$', 'filebrowser.upload_frontends.%s.views._check_file' % UPLOAD_FRONTEND, name="fb_check"),
    url(r'^upload_file/$', 'filebrowser.upload_frontends.%s.views._upload_file' % UPLOAD_FRONTEND, name="fb_do_upload"),
)
