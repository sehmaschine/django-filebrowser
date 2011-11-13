# coding: utf-8

# FILEBROWSER IMPORTS
from filebrowser.versions.settings import *
from filebrowser.versions.base import VersionFileObject
from filebrowser.fields import FileBrowseWidget as LegacyFileBrowseWidget,\
                               FileBrowseFormField as LegacyFileBrowseFormField,\
                               FileBrowseField as LegacyFileBrowseField


class VersionFileBrowseWidget(LegacyFileBrowseWidget):
    file_class = VersionFileObject
    template = "filebrowser/versions/custom_field.html"

    class Media:
        js = (os.path.join(URL_FILEBROWSER_MEDIA, 'js/AddVersionFileBrowser.js'), )
    
    def _get_extra_attrs(self):
        attrs = {}
        attrs['ADMIN_THUMBNAIL'] = ADMIN_THUMBNAIL
        return attrs


class VersionFileBrowseFormField(LegacyFileBrowseFormField):
    pass


class VersionFileBrowseField(LegacyFileBrowseField):
    description = "VersionFileBrowseField"
    file_class = VersionFileObject
    form_class = VersionFileBrowseFormField
    form_widget = VersionFileBrowseWidget


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^filebrowser\.versions\.fields\.VersionFileBrowseField"])
except ImportError:
    pass


# Provided for backwards compatibility

#FileBrowseField = VersionFileBrowseField
#FileBrowseFormField = VersionFileBrowseFormField
#FileBrowseWidget = VersionFileBrowseWidget

#try:
#    from south.modelsinspector import add_introspection_rules
#    add_introspection_rules([], ["^filebrowser\.fields\.FileBrowseField"])
#except ImportError:
#    pass
