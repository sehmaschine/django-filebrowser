# coding: utf-8

# FILEBROWSER IMPORTS
from filebrowser.versions.settings import *
from filebrowser.fields import FileBrowserWidget, FileBrowseFormField, FileBrowserField
from filebrowser.versions.base import VersionFileObject


class VersionFileBrowseWidget(FileBrowserWidget):
    file_class = VersionFileObject
    template = "filebrowser/versions/custom_field.html"
    
    def _get_extra_attrs(self):
        attrs = {}
        attrs['ADMIN_THUMBNAIL'] = ADMIN_THUMBNAIL
        return attrs


class VersionFileBrowseFormField(FileBrowseFormField):
    pass


class VersionFileBrowseField(FileBrowseField):
    description = "VersionFileBrowseField"
    form_class = VersionFileBrowseFormField
    form_widget = VersionFileBrowseWidget


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^filebrowser\.versions\.fields\.VersionFileBrowseField"])
except ImportError:
    pass
