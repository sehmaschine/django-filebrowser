# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from filebrowser.fb_settings import *
from filebrowser.models import File, ImageModification

class ImageModificationOptions(admin.ModelAdmin):
    class Media:
        js = (
            "%sjs/AddFileBrowser.js" % URL_FILEBROWSER_MEDIA,
            )
    
    save_on_top = True
    list_display = ['sysname', 'title', 'width', 'height', 'output_format']

    fieldsets = [(None, {'fields': ('sysname', 'title')}),
        (_('Dimensions'), {
            'fields': ('width', 'height', 'crop', 'crop_from')
            }),
        (_('Filters'), {
            'fields': ('color', 'brightness', 'contrast', 'sharpness', 'filters')
            }),
        (_('Masks'), {
            'fields': ('mask', 'frame')
            }),
        (_('Saving'), {
            'fields': ('output_format', 'quality')
            }),
        ]
    
#class FileOptions(admin.ModelAdmin):
#    class Media:
#        js = (
#            "%stiny_mce.js" % URL_TINYMCE,
#            "%sjs/TinyMCEAdmin.js" % URL_FILEBROWSER_MEDIA,
#            )
#    save_on_top=True

admin.site.register(ImageModification, ImageModificationOptions)
#admin.site.register(File, FileOptions)

