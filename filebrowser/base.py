# coding: utf-8

# imports
import os, shutil, re, datetime
import urlparse
import mimetypes
from time import gmtime, strftime

# django imports
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

# filebrowser imports
from filebrowser.settings import *
from filebrowser.functions import get_file_type, url_join, get_version_path, get_original_path, sort_by_attr, version_generator
from django.utils.encoding import smart_str, smart_unicode

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


class FileListing():
    """
    The FileListing represents a group of FileObjects/FileDirObjects.
    
    An example::
        
        import os
        from filebrowser.settings import MEDIA_ROOT, DIRECTORY
        from filebrowser.base import FileListing
        
        filelisting = FileListing(os.path.join(MEDIA_ROOT, DIRECTORY), sorting_by='date', sorting_order='desc')
        print filelisting.files_listing_total()
        print filelisting.results_listing_total()
        for fileobject in filelisting.files_listing_total():
            print fileobject.filetype
    """
    
    def __init__(self, path, filter_func=None, sorting_by=None, sorting_order=None):
        self.path = path
        self.filter_func = filter_func
        self.sorting_by = sorting_by
        self.sorting_order = sorting_order
    
    def listing(self):
        "List all files for path"
        if os.path.isdir(self.path):
            return (f for f in os.listdir(self.path))
        return []
    
    def walk(self):
        "Walk all files for path"
        filelisting = []
        if os.path.isdir(self.path):
            for root, dirs, files in os.walk(self.path):
                r = root.replace(os.path.join(MEDIA_ROOT, DIRECTORY),'')
                for d in dirs:
                    filelisting.append(os.path.join(r,d))
                for f in files:
                    filelisting.append(os.path.join(r,f))
        return filelisting
    
    def files_listing_total(self):
        "Returns FileObjects for all files in listing"
        files = []
        for item in self.listing():
            fileobject = FileObject(os.path.join(self.path, item))
            files.append(fileobject)
        if self.sorting_by:
            files = sort_by_attr(files, self.sorting_by)
        if self.sorting_order == "desc":
            files.reverse()
        return files
    
    def files_walk_total(self):
        "Returns FileObjects for all files in walk"
        files = []
        for item in self.walk():
            fileobject = FileObject(os.path.join(MEDIA_ROOT, DIRECTORY, item))
            files.append(fileobject)
        if self.sorting_by:
            files = sort_by_attr(files, self.sorting_by)
        if self.sorting_order == "desc":
            files.reverse()
        return files
    
    def files_listing_filtered(self):
        "Returns FileObjects for filtered files in listing"
        if self.filter_func:
            return filter(self.filter_func, self.files_listing_total())
        return self.files_listing_total()
    
    def files_walk_filtered(self):
        "Returns FileObjects for filtered files in walk"
        if self.filter_func:
            return filter(self.filter_func, self.files_walk_total())
        return self.files_walk_total()
    
    def results_listing_total(self):
        "Counter: all files"
        return len(self.files_listing_total())
    
    def results_walk_total(self):
        "Counter: all files"
        return len(self.files_walk_total())
    
    def results_listing_filtered(self):
        "Counter: filtered files"
        return len(self.files_listing_filtered())
    
    def results_walk_filtered(self):
        "Counter: filtered files"
        return len(self.files_walk_filtered())


class FileObject():
    """
    The FileObject represents a file (or directory) on the server.
    
    An example::
        
        from filebrowser.base import FileObject
        
        fileobject = FileObject(absolute_path_to_file)
    """
    
    def __init__(self, path, relative=False):
        if relative:
            self.path = os.path.join(MEDIA_ROOT, path)
        else:
            self.path = path
        self.head = os.path.dirname(path)
        self.filename = os.path.basename(path)
        self.filename_lower = self.filename.lower()
        self.filename_root = os.path.splitext(self.filename)[0]
        self.extension = os.path.splitext(self.filename)[1]
        if os.path.isdir(self.path):
            self.filetype = 'Folder'
        else:
            self.filetype = get_file_type(self.filename)
        self.mimetype = mimetypes.guess_type(self.filename)
    
    def __str__(self):
        return smart_str(self.filename)
    
    def __unicode__(self):
        return smart_unicode(self.filename)
    
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self or "None")
    
    def __len__(self):
        return len(self.url_save)
    
    # GENERAL ATTRIBUTES
    
    def _filesize(self):
        if os.path.exists(self.path):
            return os.path.getsize(self.path)
        return None
    filesize = property(_filesize)
    
    def _date(self):
        if os.path.exists(self.path):
            return os.path.getmtime(self.path)
        return None
    date = property(_date)
    
    def _datetime(self):
        if self.date:
            return datetime.datetime.fromtimestamp(self.date)
        return None
    datetime = property(_datetime)
    
    # PATH/URL ATTRIBUTES
    
    def _path_relative(self):
        "path relative to MEDIA_ROOT"
        directory_re = re.compile(r'^%s' % MEDIA_ROOT)
        return u"%s" % directory_re.sub('', self.path)
    path_relative = property(_path_relative)
    
    def _path_relative_directory(self):
        "path relative to MEDIA_ROOT + DIRECTORY"
        directory_re = re.compile(r'^%s' % os.path.join(MEDIA_ROOT,DIRECTORY))
        return u"%s" % directory_re.sub('', self.path)
    path_relative_directory = property(_path_relative_directory)
    
    def _url(self):
        "URL, including MEDIA_URL"
        return u"%s" % url_join(MEDIA_URL, self.path_relative)
    url = property(_url)
    
    def _url_relative(self):
        "URL, not including MEDIA_URL"
        directory_re = re.compile(r'^%s' % MEDIA_URL)
        return u"%s" % directory_re.sub('', self.url)
    url_relative = property(_url_relative)
    
    def _url_save(self):
        "URL which is saved to the database, e.g. using the FileBrowseField"
        if SAVE_FULL_URL:
            return self.url
        return self.url_relative
    url_save = property(_url_save)
    
    # IMAGE ATTRIBUTES
    
    def _dimensions(self):
        if self.filetype == 'Image':
            try:
                im = Image.open(self.path)
                return im.size
            except:
                pass
        return None
    dimensions = property(_dimensions)
    
    def _width(self):
        if self.dimensions:
            return self.dimensions[0]
        return None
    width = property(_width)
    
    def _height(self):
        if self.dimensions:
            return self.dimensions[1]
        return None
    height = property(_height)
    
    def _orientation(self):
        if self.dimensions:
            if self.dimensions[0] >= self.dimensions[1]:
                return "Landscape"
            else:
                return "Portrait"
        return None
    orientation = property(_orientation)
    
    # FOLDER ATTRIBUTES
    
    def _directory(self):
        directory_re = re.compile(r'^%s' % os.path.join(MEDIA_ROOT, DIRECTORY))
        return u"%s" % directory_re.sub('', self.path)
    directory = property(_directory)
    
    def _folder(self):
        directory_re = re.compile(r'^%s' % os.path.join(MEDIA_ROOT, DIRECTORY))
        return u"%s" % directory_re.sub('', self.head)
    folder = property(_folder)
    
    def _is_folder(self):
        if os.path.isdir(self.path):
            return True
        return False
    is_folder = property(_is_folder)
    
    def _is_empty(self):
        if os.path.isdir(self.path):
            if not os.listdir(self.path):
                return True
        return None
    is_empty = property(_is_empty)
    
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
            return FileObject(get_original_path(self.path))
        return None
    original = property(_original)
    
    def _versions_basedir(self):
        if VERSIONS_BASEDIR and os.path.exists(os.path.join(MEDIA_ROOT, VERSIONS_BASEDIR)):
            return os.path.join(MEDIA_ROOT, VERSIONS_BASEDIR)
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
        version_path = get_version_path(self.path, version_suffix)
        if not os.path.isfile(version_path):
            version_path = version_generator(self.path, version_suffix)
        elif os.path.getmtime(self.path) > os.path.getmtime(version_path):
            version_path = version_generator(self.path, version_suffix, force=True)
        return FileObject(version_path)
    
    # FUNCTIONS
    
    def delete(self):
        if self.is_folder:
            shutil.rmtree(self.path)
        else:
            os.remove(self.path)
    
    def delete_versions(self):
        for version in self.versions():
            try:
                os.remove(version)
            except:
                pass
    
    def delete_admin_versions(self):
        for version in self.admin_versions():
            try:
                os.remove(version)
            except:
                pass


