# coding: utf-8

# PYTHON IMPORTS
import os

# DJANGO IMPORTS
from django.db import models
from django import forms
from django.forms.widgets import Input
from django.db.models.fields import Field, CharField
from django.utils.encoding import force_unicode
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core import urlresolvers

# FILEBROWSER IMPORTS
from filebrowser.core.settings import *
from filebrowser.core.base import FileObject
from filebrowser.core.sites import site


class FileBrowseWidget(Input):
    input_type = 'text'
    file_class = FileObject
    template = "filebrowser/core/custom_field.html"
    
    class Media:
        js = (os.path.join(URL_FILEBROWSER_MEDIA, 'js/AddFileBrowser.js'), )
    
    def __init__(self, attrs=None):
        super(FileBrowseWidget, self).__init__(attrs)
        self.site = attrs.get('site', None)
        self.directory = attrs.get('directory', '')
        self.extensions = attrs.get('extensions', '')
        self.format = attrs.get('format', '')
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
        super(FileBrowseWidget, self).__init__(attrs)
        
    def _get_extra_attrs(self):
        return {}

    def render(self, name, value, attrs=None):
        url = urlresolvers.reverse(self.site.name + ":fb_browse")
        if value is None:
            value = ""
        if value != "" and not isinstance(value, self.file_class):
            value = self.file_class(value, site=self.site)
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        final_attrs['search_icon'] = URL_FILEBROWSER_MEDIA + 'img/filebrowser_icon_show.gif'
        final_attrs['url'] = url
        final_attrs['directory'] = self.directory
        final_attrs['extensions'] = self.extensions
        final_attrs['format'] = self.format
        final_attrs.update(self._get_extra_attrs())
        site = self.site
        if value != "":
            try:
                final_attrs['directory'] = os.path.split(value.original.path_relative_directory)[0]
            except:
                pass
        return render_to_string(self.template, locals())


class FileBrowseFormField(forms.CharField):
    
    default_error_messages = {
        'extension': _(u'Extension %(ext)s is not allowed. Only %(allowed)s is allowed.'),
    }
    
    def __init__(self, max_length=None, min_length=None, site=None, directory=None, extensions=None, format=None, *args, **kwargs):
        self.max_length, self.min_length = max_length, min_length
        self.site = site
        self.directory = directory
        self.extensions = extensions
        if format:
            self.format = format or ''
            self.extensions = extensions or EXTENSIONS.get(format)
        super(FileBrowseFormField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        value = super(FileBrowseFormField, self).clean(value)
        if value == '':
            return value
        file_extension = os.path.splitext(value)[1].lower()
        if self.extensions and not file_extension in self.extensions:
            raise forms.ValidationError(self.error_messages['extension'] % {'ext': file_extension, 'allowed': ", ".join(self.extensions)})
        return value


class FileBrowseField(CharField):
    description = "FileBrowseField"
    file_class = FileObject
    form_class = FileBrowseFormField
    form_widget = FileBrowseWidget
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        self.site = kwargs.pop('site', site)
        self.directory = kwargs.pop('directory', '')
        self.extensions = kwargs.pop('extensions', '')
        self.format = kwargs.pop('format', '')
        return super(FileBrowseField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        if not value or isinstance(value, self.file_class):
            return value
        return self.file_class(value, site=self.site)
    
    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return value
        return value.path

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if not value:
            return value
        return value.path
    
    def formfield(self, **kwargs):
        attrs = {}
        attrs["site"] = self.site
        attrs["directory"] = self.directory
        attrs["extensions"] = self.extensions
        attrs["format"] = self.format
        defaults = {
            'form_class': self.form_class,
            'widget': self.form_widget(attrs=attrs),
            'site': self.site,
            'directory': self.directory,
            'extensions': self.extensions,
            'format': self.format
        }
        return super(FileBrowseField, self).formfield(**defaults)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^filebrowser\.core\.fields\.FileBrowseField"])
except ImportError:
    pass
