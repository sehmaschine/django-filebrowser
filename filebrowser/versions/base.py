# coding: utf-8

# PYTHON IMPORTS
import os, shutil, re, datetime, time
import mimetypes

# DJANGO IMPORTS
from django.utils.translation import ugettext as _

# FILEBROWSER IMPORTS
from filebrowser.base import FileObject
from filebrowser.versions.settings import *
from filebrowser.versions.functions import get_file_type, url_join, get_version_path, get_original_path, sort_by_attr, version_generator, path_strip, url_strip

from django.utils.encoding import smart_str, smart_unicode

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


class VersionFileObject(FileObject):
    """
    The VersionFileObject represents a file (or directory) on the server and
    manages images versions.
    
    An example::
        
        from filebrowser.versions.base import VersionFileObject
        
        fileobject = VersionFileObject(path)
    
    where path is a relative path to a storage location.
    """
    
    # VERSIONS
    
    def _is_version(self):
        tmp = self.filename_root.split("_")
        if tmp[len(tmp)-1] in VERSIONS:
            return True
        else:
            return False
    is_version = property(_is_version)
    
    def _original(self):
        if self.is_version:
            return FileObject(get_original_path(self.path, site=self.site), site=self.site)
        return self
    original = property(_original)
    
    def _versions_basedir(self):
        if VERSIONS_BASEDIR and self.site.storage.exists(VERSIONS_BASEDIR):
            return VERSIONS_BASEDIR
        else:
            return self.head
    versions_basedir = property(_versions_basedir)
    
    def version_name(self, version_suffix):
        return self.filename_root + "_" + version_suffix + self.extension
    
    def versions(self):
        version_list = []
        if self.filetype == "Image":
            for version in VERSIONS:
                version_list.append(os.path.join(self.versions_basedir, self.version_name(version)))
        return version_list
    
    def admin_versions(self):
        version_list = []
        if self.filetype == "Image":
            for version in ADMIN_VERSIONS:
                version_list.append(os.path.join(self.versions_basedir, self.version_name(version)))
                #version_list.append(FileObject(os.path.join(self.versions_basedir, self.version_name(version))))
        return version_list
    
    def version_generate(self, version_suffix):
        version_path = get_version_path(self.path, version_suffix, site=self.site)
        if not self.site.storage.isfile(version_path):
            version_path = version_generator(self.path, version_suffix, site=self.site)
        elif self.site.storage.modified_time(self.path) > self.site.storage.modified_time(version_path):
            version_path = version_generator(self.path, version_suffix, force=True, site=self.site)
        return FileObject(version_path, site=self.site)
    
    # FUNCTIONS
        
    def delete_versions(self):
        for version in self.versions():
            try:
                self.site.storage.delete(version)
            except:
                pass
    
    def delete_admin_versions(self):
        for version in self.admin_versions():
            try:
                self.site.storage.delete(version)
            except:
                pass


