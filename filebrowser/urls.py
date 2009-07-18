from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    # ajax
    url(r'^ajax/checkfilename/', 'filebrowser.ajax.checkfilename'),
    
    # filebrowser urls
    url(r'^browse/$', 'filebrowser.views.browse', name="fb_browse"),
    url(r'^mkdir/', 'filebrowser.views.mkdir', name="fb_mkdir"),
    url(r'^upload/', 'filebrowser.views.upload', name="fb_upload"),
    url(r'^rename/$', 'filebrowser.views.rename', name="fb_rename"),
    url(r'^delete/$', 'filebrowser.views.delete', name="fb_delete"),
    url(r'^versions/$', 'filebrowser.views.versions', name="fb_versions"),

)
