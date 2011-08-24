# coding: utf-8

# imports
import os, shutil, re, datetime
import urlparse
import mimetypes
from time import gmtime, strftime, time

# django imports
from django.utils.translation import ugettext as _

# filebrowser imports
from filebrowser.settings import *
from filebrowser.functions import get_file_type, url_join, get_version_path, get_original_path, sort_by_attr, version_generator, path_strip, url_strip
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
    # Four variables to store the length of a listing obtained by various listing methods
    # (updated whenever a particular listing method is called).
    _results_listing_total = None
    _results_walk_total = None
    _results_listing_filtered = None
    _results_walk_total = None
    
    def __init__(self, path, filter_func=None, sorting_by=None, sorting_order=None, media_root=MEDIA_ROOT, directory=DIRECTORY):
        self.path = path
        self.filter_func = filter_func
        self.sorting_by = sorting_by
        self.sorting_order = sorting_order
        self.media_root = media_root
        self.media_directory = directory
    
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
                r = root.replace(os.path.join(self.media_root, self.media_directory),'')
                for d in dirs:
                    filelisting.append(os.path.join(r,d))
                for f in files:
                    filelisting.append(os.path.join(r,f))
        return filelisting
    
    # Cached results of files_listing_total (without any filters and sorting applied)
    _fileobjects_total = None
    
    def files_listing_total(self):
        "Returns FileObjects for all files in listing"
        if self._fileobjects_total == None:
            self._fileobjects_total = []
            for item in self.listing():
                fileobject = FileObject(os.path.join(self.path, item), media_root=self.media_root, directory=self.media_directory)
                self._fileobjects_total.append(fileobject)
        
        files = self._fileobjects_total
        
        if self.sorting_by:
            files = sort_by_attr(files, self.sorting_by)
        if self.sorting_order == "desc":
            files.reverse()
        
        self._results_listing_total = len(files)
        return files
    
    def files_walk_total(self):
        "Returns FileObjects for all files in walk"
        files = []
        for item in self.walk():
            fileobject = FileObject(os.path.join(self.media_root, self.media_directory, item), media_root=self.media_root, directory=self.media_directory)
            files.append(fileobject)
        if self.sorting_by:
            files = sort_by_attr(files, self.sorting_by)
        if self.sorting_order == "desc":
            files.reverse()
        self._results_walk_total = len(files)
        return files
    
    def files_listing_filtered(self):
        "Returns FileObjects for filtered files in listing"
        if self.filter_func:
            listing = filter(self.filter_func, self.files_listing_total())
        else:
            listing = self.files_listing_total()
        self._results_listing_filtered = len(listing)
        return listing
    
    def files_walk_filtered(self):
        "Returns FileObjects for filtered files in walk"
        if self.filter_func:
            listing = filter(self.filter_func, self.files_walk_total())
        else:
            listing = self.files_walk_total()
        self._results_walk_filtered = len(listing)
        return listing
    
    def results_listing_total(self):
        "Counter: all files"
        if self._results_listing_total != None:
            return self._results_listing_total
        return len(self.files_listing_total())
    
    def results_walk_total(self):
        "Counter: all files"
        if self._results_walk_total != None:
            return self._results_walk_total
        return len(self.files_walk_total())
    
    def results_listing_filtered(self):
        "Counter: filtered files"
        if self._results_listing_filtered != None:
            return self._results_listing_filtered
        return len(self.files_listing_filtered())
    
    def results_walk_filtered(self):
        "Counter: filtered files"
        if self._results_walk_filtered != None:
            return self._results_walk_filtered
        return len(self.files_walk_filtered())

class FileObject():
    """
    The FileObject represents a file (or directory) on the server.
    
    An example::
        
        from filebrowser.base import FileObject
        
        fileobject = FileObject(absolute_path_to_file)
    """
    
    def __init__(self, path, relative=False, media_root=MEDIA_ROOT, directory=DIRECTORY):
        self.media_root = media_root
        self.media_directory = directory
        if relative:
            self.path = os.path.join(self.media_root, path)
        else:
            self.path = path
        self.head = os.path.dirname(path)
        self.filename = os.path.basename(path)
        self.filename_lower = self.filename.lower()
        self.filename_root = os.path.splitext(self.filename)[0]
        self.extension = os.path.splitext(self.filename)[1]
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
    _filetype_stored = None
    def _filetype(self):
        if self._filetype_stored != None:
            return self._filetype_stored
        if os.path.isdir(self.path):
            self._filetype_stored = 'Folder'
        else:
            self._filetype_stored = get_file_type(self.filename)
        return self._filetype_stored
    filetype = property(_filetype)
    
    _filesize_stored = None
    def _filesize(self):
        if self._filesize_stored != None:
            return self._filesize_stored
        if os.path.exists(self.path):
            self._filesize_stored = os.path.getsize(self.path)
            return self._filesize_stored
        return None
    filesize = property(_filesize)
    
    _date_stored = None
    def _date(self):
        if self._date_stored != None:
            return self._date_stored
        if os.path.exists(self.path):
            self._date_stored = os.path.getmtime(self.path)
            return self._date_stored
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
        return path_strip(self.path, self.media_root)
    path_relative = property(_path_relative)
    
    def _path_relative_directory(self):
        "path relative to MEDIA_ROOT + DIRECTORY"
        return path_strip(self.path, os.path.join(self.media_root,self.media_directory))
    path_relative_directory = property(_path_relative_directory)
    
    def _url(self):
        "URL, including MEDIA_URL"
        return u"%s" % url_join(MEDIA_URL, self.path_relative)
    url = property(_url)
    
    def _url_relative(self):
        "URL, not including MEDIA_URL"
        return url_strip(self.url, MEDIA_URL)
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
        return path_strip(self.path, os.path.join(self.media_root, self.media_directory))
    directory = property(_directory)
    
    def _folder(self):
        return path_strip(self.head, os.path.join(self.media_root, self.media_directory))
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
            return FileObject(get_original_path(self.path, media_root=self.media_root, directory=self.media_directory))
        return None
    original = property(_original)
    
    def _versions_basedir(self):
        if VERSIONS_BASEDIR and os.path.exists(os.path.join(self.media_root, VERSIONS_BASEDIR)):
            return os.path.join(self.media_root, VERSIONS_BASEDIR)
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
        version_path = get_version_path(self.path, version_suffix, media_root=self.media_root, directory=self.media_directory)
        if not os.path.isfile(version_path):
            version_path = version_generator(self.path, version_suffix, media_root=self.media_root)
        elif os.path.getmtime(self.path) > os.path.getmtime(version_path):
            version_path = version_generator(self.path, version_suffix, force=True, media_root=self.media_root)
        return FileObject(version_path, media_root=self.media_root, directory=self.media_directory)
    
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


