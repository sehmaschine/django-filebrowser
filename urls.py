from django.conf.urls.defaults import *

urlpatterns = patterns('filebrowser.views',
    
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/mkdir/', 'mkdir'),
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/upload/', 'upload'),
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/delete/$', 'delete'),
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/makethumbs/$', 'makethumb'),
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/makethumb/(?P<file_name>[a-zA-Z0-9._-]+)', 'makethumb'),
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/rename/(?P<file_name>[a-zA-Z0-9._-]+)', 'rename'),
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/snipshot_callback/$', 'snipshot_callback'),
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/picnik_callback/$', 'picnik_callback'),
    (r'^mkdir/', 'mkdir'),
    (r'^upload/', 'upload'),
    (r'^delete/$', 'delete'),
    (r'^makethumbs/$', 'makethumb'),
    (r'^makethumb/(?P<file_name>[a-zA-Z0-9._-]+)', 'makethumb'),
    (r'^rename/(?P<file_name>[a-zA-Z0-9._-]+)', 'rename'),
    (r'^snipshot_callback/$', 'snipshot_callback'),
    (r'^picnik_callback/$', 'picnik_callback'),
    (r'^(?P<dir_name>[_a-zA-Z0-9./-]+)/$', 'index'),
    (r'^$', 'index'),

)
