# coding: utf-8

"""
A custom FileBrowseField.
"""

from django.db import models
from django import forms
from django.forms.widgets import Input
from django.db.models.fields import Field, CharField
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode, smart_unicode, smart_str
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import EMPTY_VALUES
from django.conf import settings

import os
import re

from filebrowser.functions import _get_file_type, _url_join
from filebrowser.fb_settings import *
from filebrowser.views import FileObject


def dir_from_url(url):
    """
    Get the relative server directory from a URL.
        e.g. /media/uploads/blog/2009/myphoto.jpg
        returns /blog/2009/
        e.g. uploads/blog/2009/06/
        return /blog/2009/
    """
    
    rel_from_media_url = URL_WWW.replace(settings.MEDIA_URL, "", 1)
    if url.startswith(URL_WWW):
        value = os.path.split(url)[0].replace(URL_WWW, "", 1)
    elif url.startswith(rel_from_media_url):
        value = os.path.split(url)[0].replace(rel_from_media_url, "", 1)
    else:
        value = URL_WWW
    return value
    

class FileBrowseWidget(Input):
    input_type = 'text'
    
    class Media:
        js = (os.path.join(URL_FILEBROWSER_MEDIA, 'js/AddFileBrowser.js'), )
    
    def __init__(self, attrs=None):
        self.initial_directory = attrs.get('initial_directory')
        self.extensions_allowed = attrs.get('extensions_allowed')
        self.format = attrs.get('format') or ''
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
    
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif not isinstance(value, (str, unicode)):
            value = value.original
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        final_attrs['search_icon'] = URL_FILEBROWSER_MEDIA + 'img/filebrowser_icon_show.gif'
        final_attrs['format'] = self.format
        if value != "":
            final_attrs['initial_directory'] = _url_join(URL_ADMIN, dir_from_url(value))
            final_attrs['value'] = force_unicode(value)
            try:
                final_attrs['file'] = FileObject(os.path.split(value)[1], dir_from_url(value))
            except:
                pass
        else:
            final_attrs['initial_directory'] = _url_join(URL_ADMIN, final_attrs['initial_directory'])
        return render_to_string("filebrowser/custom_field.html", locals())
    

class FileBrowseFormField(forms.CharField):
    widget = FileBrowseWidget
    
    default_error_messages = {
    'extension': _(u'Extension %(ext)s is not allowed. Only %(allowed)s is allowed.'),
    }
    
    def __init__(self, max_length=None, min_length=None,
                 initial_directory=None, extensions_allowed=None, format=None,
                 *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        self.initial_directory = initial_directory
        self.extensions_allowed = extensions_allowed
        if format:
            self.format = format or ''
            self.extensions_allowed = extensions_allowed or EXTENSIONS.get(format)
        super(FileBrowseFormField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        value = super(FileBrowseFormField, self).clean(value)
        if value == '':
            return value
        file_extension = os.path.splitext(value)[1].lower()
        if self.extensions_allowed and not file_extension in self.extensions_allowed:
            raise forms.ValidationError(self.error_messages['extension'] % {'ext': file_extension, 'allowed': ", ".join(self.extensions_allowed)})
        return value
    

class FileBrowserImageSize(object):
    
    def __init__(self, image_type, original):
        self.image_type = image_type
        self.original = original
        
    def __unicode__(self):
        return u'%s' % (self._get_image())
        
    def _get_image(self):
        if not hasattr(self, '_image_cache'):
            self._image_cache = self._get_image_name()
        return self._image_cache
        
    def _get_image_name(self):
        arg = self.image_type
        value = self.original
        value_re = re.compile(r'^(%s)' % (URL_WWW))
        value_path = value_re.sub('', value)
        filename = os.path.split(value_path)[1]
        if CHECK_EXISTS:
            path = os.path.split(value_path)[0]
            if os.path.isfile(os.path.join(PATH_SERVER, path, filename.replace(".", "_").lower() + IMAGE_GENERATOR_DIRECTORY, arg + filename)):
                #img_value = '/'.join(os.path.split(value)[0], filename.replace(".", "_").lower() + IMAGE_GENERATOR_DIRECTORY, arg + filename)
                img_value = '/'.join((os.path.split(value)[0], filename.replace(".", "_").lower() + IMAGE_GENERATOR_DIRECTORY, arg + filename))
                return u'%s' % (img_value)
            else:
                return u''
        else:
            img_value = '/'.join((os.path.split(value)[0], filename.replace(".", "_").lower() + IMAGE_GENERATOR_DIRECTORY, arg + filename))
            return u'%s' % (img_value)
        

class FileBrowserImageType(object):
    
    def __init__(self, original, image_list):
        for image_type in image_list:
            setattr(self, image_type[0].rstrip('_'), FileBrowserImageSize(image_type[0], original))
        

class FileBrowserFile(object):
    
    def __init__(self, value):
        self.original = value
        self._add_image_types()
    
    def _add_image_types(self):
        all_prefixes = []
        for imgtype in IMAGE_GENERATOR_LANDSCAPE:
            if imgtype[0] not in all_prefixes:
                all_prefixes.append(imgtype[0])
                setattr(self, imgtype[0].rstrip('_'), FileBrowserImageSize(imgtype[0], self.original))
        for imgtype in IMAGE_GENERATOR_PORTRAIT:
            if imgtype[0] not in all_prefixes:
                all_prefixes.append(imgtype[0])
                setattr(self, imgtype[0].rstrip('_'), FileBrowserImageSize(imgtype[0], self.original))
        for imgtype in IMAGE_CROP_GENERATOR:
            if imgtype[0] not in all_prefixes:
                all_prefixes.append(imgtype[0])
                setattr(self, imgtype[0].rstrip('_'), FileBrowserImageSize(imgtype[0], self.original))
    
    def __unicode__(self):
        return self.original
    
    def crop(self):
        if not hasattr(self, '_crop_cache'):
            self._crop_cache = FileBrowserImageType(self.original, IMAGE_CROP_GENERATOR)
        return self._crop_cache
    

class FileBrowseField(Field):
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, verbose_name=None, initial_directory=None, extensions_allowed=None, format=None, *args, **kwargs):
        self.initial_directory = initial_directory or '/'
        self.extensions_allowed = extensions_allowed or ''
        self.format = format or ''
        return super(FileBrowseField, self).__init__(verbose_name=verbose_name, *args, **kwargs)
    
    def to_python(self, value):
        if not value or isinstance(value, FileBrowserFile):
            return value
        return FileBrowserFile(value)
    
    def get_db_prep_value(self, value):
        return getattr(value, 'original', value)
    
    def get_manipulator_field_objs(self):
        return [oldforms.TextField]
    
    def get_internal_type(self):
        return "CharField"
    
    def formfield(self, **kwargs):
        attrs = {}
        attrs["initial_directory"] = self.initial_directory
        attrs["extensions_allowed"] = self.extensions_allowed
        attrs["format"] = self.format
        defaults = {'max_length': self.max_length}
        defaults['form_class'] = FileBrowseFormField
        defaults['widget'] = FileBrowseWidget(attrs=attrs)
        defaults['initial_directory'] = self.initial_directory
        defaults['extensions_allowed'] = self.extensions_allowed
        defaults['format'] = self.format
        return super(FileBrowseField, self).formfield(**defaults)
    

