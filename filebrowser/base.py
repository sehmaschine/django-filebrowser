# coding: utf-8

# PYTHON IMPORTS
import os, shutil, re, datetime, time, platform
import mimetypes

# DJANGO IMPORTS
from django.utils.translation import ugettext as _

# FILEBROWSER IMPORTS
from filebrowser.settings import VERSIONS, ADMIN_VERSIONS, VERSIONS_BASEDIR, FORCE_PLACEHOLDER, SHOW_PLACEHOLDER, STRICT_PIL
from filebrowser.functions import get_file_type, url_join, get_version_path, get_original_path, version_generator, path_strip, url_strip
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
        
        from filebrowser.base import FileListing
        filelisting = FileListing(path, sorting_by='date', sorting_order='desc')
        print filelisting.files_listing_total()
        print filelisting.results_listing_total()
        for fileobject in filelisting.files_listing_total():
            print fileobject.filetype

    where path is a relative path to a storage location
    """
    # Four variables to store the length of a listing obtained by various listing methods
    # (updated whenever a particular listing method is called).
    _results_listing_total = None
    _results_walk_total = None
    _results_listing_filtered = None
    _results_walk_total = None
    
    def __init__(self, path, filter_func=None, sorting_by=None, sorting_order=None, site=None):
        self.path = path
        self.filter_func = filter_func
        self.sorting_by = sorting_by
        self.sorting_order = sorting_order
        if not site:
            from filebrowser.sites import site as default_site
            site = default_site
        self.site = site

    def sort_by_attr(self, seq, attr):
        """
        Sort the sequence of objects by object's attribute
        
        Arguments:
        seq  - the list or any sequence (including immutable one) of objects to sort.
        attr - the name of attribute to sort by
        
        Returns:
        the sorted list of objects.
        """
        import operator
        
        # Use the "Schwartzian transform"
        # Create the auxiliary list of tuples where every i-th tuple has form
        # (seq[i].attr, i, seq[i]) and sort it. The second item of tuple is needed not
        # only to provide stable sorting, but mainly to eliminate comparison of objects
        # (which can be expensive or prohibited) in case of equal attribute values.
        intermed = map(None, map(getattr, seq, (attr,)*len(seq)), xrange(len(seq)), seq)
        intermed.sort()
        return map(operator.getitem, intermed, (-1,) * len(intermed))

    _is_folder_stored = None
    def _is_folder(self):
        if self._is_folder_stored == None:
            self._is_folder_stored = self.site.storage.isdir(self.path)
        return self._is_folder_stored
    is_folder = property(_is_folder)

    def listing(self):
        "List all files for path"
        if self.is_folder:
            dirs, files = self.site.storage.listdir(self.path)
            return (f for f in dirs + files)
        return []

    def _walk(self, path, filelisting):
        """
        Recursively walks the path and collects all files and
        directories.

        Danger: Symbolic links can create cycles and this function
        ends up in a regression.
        """
        dirs, files = self.site.storage.listdir(path)

        if dirs:
            for d in dirs:
                self._walk(os.path.join(path, d), filelisting)
                filelisting.extend([path_strip(os.path.join(path,d), self.site.directory)])

        if files:
            for f in files:
                filelisting.extend([path_strip(os.path.join(path,f), self.site.directory)])

    
    def walk(self):
        "Walk all files for path"
        filelisting = []
        if self.is_folder:
            self._walk(self.path, filelisting)
        return filelisting
    
    # Cached results of files_listing_total (without any filters and sorting applied)
    _fileobjects_total = None
    
    def files_listing_total(self):
        "Returns FileObjects for all files in listing"
        if self._fileobjects_total == None:
            self._fileobjects_total = []
            for item in self.listing():
                fileobject = FileObject(os.path.join(self.path, item), site=self.site)
                self._fileobjects_total.append(fileobject)
        
        files = self._fileobjects_total
        
        if self.sorting_by:
            files = self.sort_by_attr(files, self.sorting_by)
        if self.sorting_order == "desc":
            files.reverse()
        
        self._results_listing_total = len(files)
        return files
    
    def files_walk_total(self):
        "Returns FileObjects for all files in walk"
        files = []
        for item in self.walk():
            fileobject = FileObject(os.path.join(self.site.directory, item), site=self.site)
            files.append(fileobject)
        if self.sorting_by:
            files = self.sort_by_attr(files, self.sorting_by)
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
        fileobject = FileObject(path)
    
    where path is a relative path to a storage location
    """
    
    def __init__(self, path, site=None):
        if not site:
            from filebrowser.sites import site as default_site
            site = default_site
        self.site = site
        if platform.system() == 'Windows':
            self.path = path.replace('\\','/')
        else:
            self.path = path
        self.head = os.path.dirname(path)
        self.filename = os.path.basename(path)
        self.filename_lower = self.filename.lower()
        self.filename_root, self.extension = os.path.splitext(self.filename)
        self.mimetype = mimetypes.guess_type(self.filename)
    
    def __str__(self):
        return smart_str(self.path)
    
    def __unicode__(self):
        return smart_unicode(self.path)
    
    @property
    def name(self):
        return self.path

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self or "None")
    
    def __len__(self):
        return len(self.path)
    
    # GENERAL ATTRIBUTES
    # filetype
    # filesize
    # date
    # datetime
    # exists

    _filetype_stored = None
    def _filetype(self):
        "Filetype as defined with EXTENSIONS"
        if self._filetype_stored != None:
            return self._filetype_stored
        if self.is_folder:
            self._filetype_stored = 'Folder'
        else:
            self._filetype_stored = get_file_type(self.filename)
        return self._filetype_stored
    filetype = property(_filetype)
    
    _filesize_stored = None
    def _filesize(self):
        "Filesize in bytes"
        if self._filesize_stored != None:
            return self._filesize_stored
        if self.exists():
            self._filesize_stored = self.site.storage.size(self.path)
            return self._filesize_stored
        return None
    filesize = property(_filesize)
    
    _date_stored = None
    def _date(self):
        "Modified time (from site.storage) as float (mktime)"
        if self._date_stored != None:
            return self._date_stored
        if self.exists():
            self._date_stored = time.mktime(self.site.storage.modified_time(self.path).timetuple())
            return self._date_stored
        return None
    date = property(_date)
    
    def _datetime(self):
        "Modified time (from site.storage) as datetime"
        if self.date:
            return datetime.datetime.fromtimestamp(self.date)
        return None
    datetime = property(_datetime)

    _exists_stored = None
    def exists(self):
        "True, if the path exists, False otherwise"
        if self._exists_stored == None:
            self._exists_stored = self.site.storage.exists(self.path)
        return self._exists_stored
    
    # PATH/URL ATTRIBUTES
    # path (see init)
    # path_relative_directory
    # path_full
    # dirname
    # url
    
    def _path_relative_directory(self):
        "Server path relative to site.directory"
        return path_strip(self.path, self.site.directory)
    path_relative_directory = property(_path_relative_directory)

    def _path_full(self):
        "Full path as defined with site.storage"
        return self.site.storage.path(self.path)
    path_full = property(_path_full)

    def _dirname(self):
        "The directory (not including site.directory)"
        return os.path.dirname(self.path_relative_directory)
    dirname = property(_dirname)

    def _url(self):
        "URL for the file/folder as defined with site.storage"
        return self.site.storage.url(self.path)
    url = property(_url)

    # IMAGE ATTRIBUTES
    # dimensions
    # width
    # height
    # aspectratio
    # orientation

    _dimensions_stored = None
    def _dimensions(self):
        "Image dimensions as a tuple"
        if self.filetype != 'Image':
            return None
        if self._dimensions_stored != None:
            return self._dimensions_stored
        try:
            im = Image.open(self.site.storage.open(self.path))
            self._dimensions_stored = im.size
        except:
            pass
        return self._dimensions_stored
    dimensions = property(_dimensions)

    def _width(self):
        "Image width in px"
        if self.dimensions:
            return self.dimensions[0]
        return None
    width = property(_width)
    
    def _height(self):
        "Image height in px"
        if self.dimensions:
            return self.dimensions[1]
        return None
    height = property(_height)

    def _aspectratio(self):
        "Aspect ratio (float format)"
        if self.dimensions:
            return float(self.width)/float(self.height)
        return None
    aspectratio = property(_aspectratio)
    
    def _orientation(self):
        "Image orientation, either 'Landscape' or 'Portrait'"
        if self.dimensions:
            if self.dimensions[0] >= self.dimensions[1]:
                return "Landscape"
            else:
                return "Portrait"
        return None
    orientation = property(_orientation)
    
    # FOLDER ATTRIBUTES
    # directory
    # folder
    # is_folder
    # is_empty
    
    def _directory(self):
        "Folder(s) relative from site.directory" # FIXME: needed/rename?
        return path_strip(self.path, self.site.directory)
    directory = property(_directory)
    
    def _folder(self):
        "Parent folder(s)" # FIXME: needed/rename?
        return os.path.dirname(path_strip(os.path.join(self.head,''), self.site.directory))
    folder = property(_folder)
    
    _is_folder_stored = None
    def _is_folder(self):
        "True, if path is a folder"
        if self._is_folder_stored == None:
            self._is_folder_stored = self.site.storage.isdir(self.path)
        return self._is_folder_stored
    is_folder = property(_is_folder)
    
    def _is_empty(self):
        "True, if folder is empty"
        if self.is_folder:
            dirs, files = self.site.storage.listdir(self.path)
            if not dirs and not files:
                return True
        return False
    is_empty = property(_is_empty)
    
    # VERSIONS
    # is_version
    # original
    # versions_basedir
    # versions
    # admin_versions
    # version_name(suffix)
    # version_generate(suffix)
    
    def _is_version(self):
        "True if file is a version, false otherwise"
        tmp = self.filename_root.split("_")
        if tmp[len(tmp)-1] in VERSIONS:
            return True
        else:
            return False
    is_version = property(_is_version)
    
    def _original(self):
        "Returns the original FileObject"
        if self.is_version:
            return FileObject(get_original_path(self.path, site=self.site), site=self.site)
        return self
    original = property(_original)
    
    def _versions_basedir(self):
        "Main directory for storing versions (either VERSIONS_BASEDIR or site.directory)"
        if VERSIONS_BASEDIR:
            return VERSIONS_BASEDIR
        elif self.site.directory:
            return self.site.directory
        else:
            return ""
    versions_basedir = property(_versions_basedir)
    
    def versions(self):
        "List of versions (not checking if they actually exist)"
        version_list = []
        if self.filetype == "Image":
            for version in VERSIONS:
                version_list.append(os.path.join(self.versions_basedir, self.folder, self.version_name(version)))
        return version_list
    
    def admin_versions(self):
        "List of admin versions (not checking if they actually exist)"
        version_list = []
        if self.filetype == "Image":
            for version in ADMIN_VERSIONS:
                version_list.append(os.path.join(self.versions_basedir, self.folder, self.version_name(version)))
        return version_list

    def version_name(self, version_suffix):
        "Name of a version, depending on the suffix"
        return self.filename_root + "_" + version_suffix + self.extension

    def version_generate(self, version_suffix):
        "Generate a version, depending on the suffix"
        path = self.path

        if FORCE_PLACEHOLDER or (
            SHOW_PLACEHOLDER and not self.site.storage.isfile(path)):
            path = PLACEHOLDER
        
        version_path = get_version_path(path, version_suffix, site=self.site)

        if not self.site.storage.isfile(version_path):
            version_path = version_generator(path, version_suffix, site=self.site)
        elif self.site.storage.modified_time(path) > self.site.storage.modified_time(version_path):
            version_path = version_generator(path, version_suffix, force=True, site=self.site)

        return FileObject(version_path, site=self.site)
    
    # DELETE FUNCTIONS
    # delete
    # delete_versions
    # delete_admin_versions
    
    def delete(self):
        "Delete FileObject (deletes a folder recursively)"
        if self.is_folder:
            self.site.storage.rmtree(self.path)
        else:
            self.site.storage.delete(self.path)
    
    def delete_versions(self):
        "Delete versions"
        for version in self.versions():
            try:
                self.site.storage.delete(version)
            except:
                pass
    
    def delete_admin_versions(self):
        "Delete admin versions"
        for version in self.admin_versions():
            try:
                self.site.storage.delete(version)
            except:
                pass

