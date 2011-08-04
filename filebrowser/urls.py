from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    # filebrowser urls
    url(r'^browse/$', 'filebrowser.views.browse', name="fb_browse"),
    url(r'^createdir/', 'filebrowser.views.createdir', name="fb_createdir"),
    url(r'^upload/', 'filebrowser.views.upload', name="fb_upload"),
    url(r'^delete_confirm/$', 'filebrowser.views.delete_confirm', name="fb_delete_confirm"),
    url(r'^delete/$', 'filebrowser.views.delete', name="fb_delete"),
    url(r'^detail/$', 'filebrowser.views.detail', name="fb_detail"),
    url(r'^version/$', 'filebrowser.views.version', name="fb_version"),
    
    url(r'^check_file/$', 'filebrowser.views._check_file', name="fb_check"),
    url(r'^upload_file/$', 'filebrowser.views._upload_file', name="fb_do_upload"),
    
)
