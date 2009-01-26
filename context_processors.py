# -*- coding: UTF-8 -*-
from django.conf import settings

from filebrowser.fb_settings import *

def filebrowser(request=None):
    d = {
        'FILEBROWSER_URL_WWW': URL_WWW,
        'FILEBROWSER_URL_ADMIN': URL_ADMIN,
        }
    return d
