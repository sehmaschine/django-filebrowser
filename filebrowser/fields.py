# coding: utf-8

# FILEBROWSER IMPORTS
from filebrowser.settings import *
from filebrowser.base import FileObject
from filebrowser.core.fields import FileBrowseWidget as CoreFileBrowseWidget,\
                                    FileBrowseFormField as CoreFileBrowseFormField,\
                                    FileBrowseField as CoreFileBrowseField


class FileBrowseWidget(CoreFileBrowseWidget):
    file_class = FileObject
    template = "filebrowser/custom_field.html"

    class Media:
        js = (os.path.join(URL_FILEBROWSER_MEDIA, 'js/AddVersionFileBrowser.js'), )
    
    def _get_extra_attrs(self):
        attrs = {}
        attrs['ADMIN_THUMBNAIL'] = ADMIN_THUMBNAIL
        return attrs


class FileBrowseFormField(CoreFileBrowseFormField):
    pass


class FileBrowseField(CoreFileBrowseField):
    description = "FileBrowseField"
    file_class = FileObject
    form_class = FileBrowseFormField
    form_widget = FileBrowseWidget


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^filebrowser\.fields\.FileBrowseField"])
except ImportError:
    pass
