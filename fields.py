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

import os

from filebrowser.functions import _get_file_type
from filebrowser.fb_settings import *

class FileBrowseFormField(forms.Field):
    default_error_messages = {
        'max_length': _(u'Ensure this value has at most %(max)d characters (it has %(length)d).'),
        'min_length': _(u'Ensure this value has at least %(min)d characters (it has %(length)d).'),
        'extension': _(u'Extension %(ext)s is not allowed. Only %(allowed)s is allowed.'),
    }
    
    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        self.initial_directory = kwargs['initial_directory']
        self.extensions_allowed = kwargs['extensions_allowed']
        print "kwargs: ", kwargs
        del kwargs['initial_directory']
        del kwargs['extensions_allowed']
        super(FileBrowseFormField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        "Validates max_length and min_length. Returns a Unicode object. Validates extension ..."
        super(FileBrowseFormField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        value = smart_unicode(value)
        value_length = len(value)
        if self.max_length is not None and value_length > self.max_length:
            raise forms.ValidationError(self.error_messages['max_length'] % {'max': self.max_length, 'length': value_length})
        if self.min_length is not None and value_length < self.min_length:
            raise forms.ValidationError(self.error_messages['min_length'] % {'min': self.min_length, 'length': value_length})
        file_extension = os.path.splitext(value)[1].lower()
        if self.extensions_allowed and not file_extension in self.extensions_allowed:
            raise forms.ValidationError(self.error_messages['extension'] % {'ext': file_extension, 'allowed': ", ".join(self.extensions_allowed)})
        return value
    

class FileBrowseWidget(Input):
    input_type = 'text'
    
    def __init__(self, attrs=None):
        self.initial_directory = attrs['initial_directory']
        self.extensions_allowed = attrs['extensions_allowed']
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
    
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
            file = os.path.split(value)[1]
            path = os.path.split(value)[0].replace(URL_WWW, "")
            file_type = _get_file_type(file)
            path_thumb = ""
            if file_type == 'Image':
                # check if thumbnail exists
                if os.path.isfile(os.path.join(PATH_SERVER, path, THUMB_PREFIX + file)):
                    path_thumb = os.path.join(os.path.split(value)[0], THUMB_PREFIX + file)
                else:
                    path_thumb = settings.ADMIN_MEDIA_PREFIX + 'filebrowser/img/filebrowser_Thumb.gif'
            elif file_type == "Folder":
                path_thumb = ""
            else:
                # if file is not an image, display file-icon (which is linked to the file) instead
                path_thumb = settings.ADMIN_MEDIA_PREFIX + 'filebrowser/img/filebrowser_' + file_type + '.gif'
            final_attrs['thumbnail'] = path_thumb
        return render_to_string("filebrowser/custom_field.html", locals())
    

class FileBrowseField(Field):
    __metaclass__ = models.SubfieldBase
    
    def get_manipulator_field_objs(self):
        return [oldforms.TextField]
    
    def get_internal_type(self):
        return "CharField"
    
    def formfield(self, **kwargs):
        attrs = {}
        attrs["initial_directory"] = self.initial_directory
        attrs["extensions_allowed"] = self.extensions_allowed
        defaults = {'max_length': self.max_length}
        defaults['form_class'] = FileBrowseFormField
        defaults['widget'] = FileBrowseWidget(attrs=attrs)
        kwargs['initial_directory'] = self.initial_directory
        kwargs['extensions_allowed'] = self.extensions_allowed
        defaults.update(kwargs)
        return super(FileBrowseField, self).formfield(**defaults)
    
    def __init__(self, *args, **kwargs):
        self.initial_directory = kwargs['initial_directory']
        self.extensions_allowed = kwargs['extensions_allowed']
        del kwargs['initial_directory']
        del kwargs['extensions_allowed']
        return super(FileBrowseField, self).__init__(*args, **kwargs)
    

