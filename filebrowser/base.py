# coding: utf-8

import datetime
import mimetypes
import os
import platform
import tempfile
import time
import warnings

from django.core.files import File
from django.utils.encoding import python_2_unicode_compatible, smart_str
from django.utils.six import string_types

from filebrowser.settings import EXTENSIONS, VERSIONS, ADMIN_VERSIONS, VERSIONS_BASEDIR, VERSION_QUALITY, STRICT_PIL, IMAGE_MAXBLOCK, DEFAULT_PERMISSIONS
from filebrowser.utils import path_strip, scale_and_crop

if STRICT_PIL:
    from PIL import Image
    from PIL import ImageFile
else:
    try:
        from PIL import Image
        from PIL import ImageFile
    except ImportError:
        import Image
        import ImageFile


ImageFile.MAXBLOCK = IMAGE_MAXBLOCK  # default is 64k


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

    # HELPER METHODS
    # sort_by_attr

    def sort_by_attr(self, seq, attr):
        """
        Sort the sequence of objects by object's attribute

        Arguments:
        seq  - the list or any sequence (including immutable one) of objects to sort.
        attr - the name of attribute to sort by

        Returns:
        the sorted list of objects.
        """
        from operator import attrgetter
        if isinstance(attr, string_types):  # Backward compatibility hack
            attr = (attr, )
        return sorted(seq, key=attrgetter(*attr))

    _is_folder_stored = None
    @property
    def is_folder(self):
        if self._is_folder_stored is None:
            self._is_folder_stored = self.site.storage.isdir(self.path)
        return self._is_folder_stored

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
                filelisting.extend([path_strip(os.path.join(path, d), self.site.directory)])

        if files:
            for f in files:
                filelisting.extend([path_strip(os.path.join(path, f), self.site.directory)])

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
        if self._fileobjects_total is None:
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
            listing = list(filter(self.filter_func, self.files_listing_total()))
        else:
            listing = self.files_listing_total()
        self._results_listing_filtered = len(listing)
        return listing

    def files_walk_filtered(self):
        "Returns FileObjects for filtered files in walk"
        if self.filter_func:
            listing = list(filter(self.filter_func, self.files_walk_total()))
        else:
            listing = self.files_walk_total()
        self._results_walk_filtered = len(listing)
        return listing

    def results_listing_total(self):
        "Counter: all files"
        if self._results_listing_total is not None:
            return self._results_listing_total
        return len(self.files_listing_total())

    def results_walk_total(self):
        "Counter: all files"
        if self._results_walk_total is not None:
            return self._results_walk_total
        return len(self.files_walk_total())

    def results_listing_filtered(self):
        "Counter: filtered files"
        if self._results_listing_filtered is not None:
            return self._results_listing_filtered
        return len(self.files_listing_filtered())

    def results_walk_filtered(self):
        "Counter: filtered files"
        if self._results_walk_filtered is not None:
            return self._results_walk_filtered
        return len(self.files_walk_filtered())


@python_2_unicode_compatible
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
            self.path = path.replace('\\', '/')
        else:
            self.path = path
        self.head = os.path.dirname(path)
        self.filename = os.path.basename(path)
        self.filename_lower = self.filename.lower()
        self.filename_root, self.extension = os.path.splitext(self.filename)
        self.mimetype = mimetypes.guess_type(self.filename)

    def __str__(self):
        return smart_str(self.path)

    @property
    def name(self):
        return self.path

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self or "None")

    def __len__(self):
        return len(self.path)

    # HELPER METHODS
    # _get_file_type

    def _get_file_type(self):
        "Get file type as defined in EXTENSIONS."
        file_type = ''
        for k, v in EXTENSIONS.items():
            for extension in v:
                if self.extension.lower() == extension.lower():
                    file_type = k
        return file_type

    # GENERAL ATTRIBUTES/PROPERTIES
    # filetype
    # filesize
    # date
    # datetime
    # exists

    _filetype_stored = None
    @property
    def filetype(self):
        "Filetype as defined with EXTENSIONS"
        if self._filetype_stored is not None:
            return self._filetype_stored
        if self.is_folder:
            self._filetype_stored = 'Folder'
        else:
            self._filetype_stored = self._get_file_type()
        return self._filetype_stored

    _filesize_stored = None
    @property
    def filesize(self):
        "Filesize in bytes"
        if self._filesize_stored is not None:
            return self._filesize_stored
        if self.exists:
            self._filesize_stored = self.site.storage.size(self.path)
            return self._filesize_stored
        return None

    _date_stored = None
    @property
    def date(self):
        "Modified time (from site.storage) as float (mktime)"
        if self._date_stored is not None:
            return self._date_stored
        if self.exists:
            self._date_stored = time.mktime(self.site.storage.modified_time(self.path).timetuple())
            return self._date_stored
        return None

    @property
    def datetime(self):
        "Modified time (from site.storage) as datetime"
        if self.date:
            return datetime.datetime.fromtimestamp(self.date)
        return None

    _exists_stored = None
    @property
    def exists(self):
        "True, if the path exists, False otherwise"
        if self._exists_stored is None:
            self._exists_stored = self.site.storage.exists(self.path)
        return self._exists_stored

    # PATH/URL ATTRIBUTES/PROPERTIES
    # path (see init)
    # path_relative_directory
    # path_full
    # dirname
    # url

    @property
    def path_relative_directory(self):
        "Path relative to site.directory"
        return path_strip(self.path, self.site.directory)

    @property
    def path_full(self):
        "Absolute path as defined with site.storage"
        return self.site.storage.path(self.path)

    @property
    def dirname(self):
        "The directory (not including site.directory)"
        return os.path.dirname(self.path_relative_directory)

    @property
    def url(self):
        "URL for the file/folder as defined with site.storage"
        return self.site.storage.url(self.path)

    # IMAGE ATTRIBUTES/PROPERTIES
    # dimensions
    # width
    # height
    # aspectratio
    # orientation

    _dimensions_stored = None
    @property
    def dimensions(self):
        "Image dimensions as a tuple"
        if self.filetype != 'Image':
            return None
        if self._dimensions_stored is not None:
            return self._dimensions_stored
        try:
            im = Image.open(self.site.storage.open(self.path))
            self._dimensions_stored = im.size
        except:
            pass
        return self._dimensions_stored

    @property
    def width(self):
        "Image width in px"
        if self.dimensions:
            return self.dimensions[0]
        return None

    @property
    def height(self):
        "Image height in px"
        if self.dimensions:
            return self.dimensions[1]
        return None

    @property
    def aspectratio(self):
        "Aspect ratio (float format)"
        if self.dimensions:
            return float(self.width) / float(self.height)
        return None

    @property
    def orientation(self):
        "Image orientation, either 'Landscape' or 'Portrait'"
        if self.dimensions:
            if self.dimensions[0] >= self.dimensions[1]:
                return "Landscape"
            else:
                return "Portrait"
        return None

    # FOLDER ATTRIBUTES/PROPERTIES
    # directory (deprecated)
    # folder (deprecated)
    # is_folder
    # is_empty

    @property
    def directory(self):
        "Folder(s) relative from site.directory"
        warnings.warn("directory will be removed with 3.6, use path_relative_directory instead.", DeprecationWarning)
        return path_strip(self.path, self.site.directory)

    @property
    def folder(self):
        "Parent folder(s)"
        warnings.warn("directory will be removed with 3.6, use dirname instead.", DeprecationWarning)
        return os.path.dirname(path_strip(os.path.join(self.head, ''), self.site.directory))

    _is_folder_stored = None
    @property
    def is_folder(self):
        "True, if path is a folder"
        if self._is_folder_stored is None:
            self._is_folder_stored = self.site.storage.isdir(self.path)
        return self._is_folder_stored

    @property
    def is_empty(self):
        "True, if folder is empty. False otherwise, or if the object is not a folder."
        if self.is_folder:
            dirs, files = self.site.storage.listdir(self.path)
            if not dirs and not files:
                return True
        return False

    # VERSION ATTRIBUTES/PROPERTIES
    # is_version
    # versions_basedir
    # original
    # original_filename

    @property
    def is_version(self):
        "True if file is a version, false otherwise"
        # FIXME: with 3.7, check for VERSIONS_BASEDIR as well in order to make sure
        # it is actually a version (do not rely on the file ending only).
        tmp = self.filename_root.split("_")
        if tmp[len(tmp) - 1] in VERSIONS:
            return True
        return False

    @property
    def versions_basedir(self):
        "Main directory for storing versions (either VERSIONS_BASEDIR or site.directory)"
        if VERSIONS_BASEDIR:
            return VERSIONS_BASEDIR
        elif self.site.directory:
            return self.site.directory
        else:
            return ""

    @property
    def original(self):
        "Returns the original FileObject"
        if self.is_version:
            relative_path = self.head.replace(self.versions_basedir, "").lstrip("/")
            return FileObject(os.path.join(self.site.directory, relative_path, self.original_filename), site=self.site)
        return self

    @property
    def original_filename(self):
        "Get the filename of an original image from a version"
        tmp = self.filename_root.split("_")
        if tmp[len(tmp) - 1] in VERSIONS:
            return u"%s%s" % (self.filename_root.replace("_%s" % tmp[len(tmp) - 1], ""), self.extension)
        return self.filename

    # VERSION METHODS
    # versions()
    # admin_versions()
    # version_name(suffix)
    # version_path(suffix)
    # version_generate(suffix)

    def versions(self):
        "List of versions (not checking if they actually exist)"
        version_list = []
        if self.filetype == "Image" and not self.is_version:
            for version in sorted(VERSIONS):
                version_list.append(os.path.join(self.versions_basedir, self.dirname, self.version_name(version)))
        return version_list

    def admin_versions(self):
        "List of admin versions (not checking if they actually exist)"
        version_list = []
        if self.filetype == "Image" and not self.is_version:
            for version in ADMIN_VERSIONS:
                version_list.append(os.path.join(self.versions_basedir, self.dirname, self.version_name(version)))
        return version_list

    def version_name(self, version_suffix):
        "Name of a version"  # FIXME: version_name for version?
        return self.filename_root + "_" + version_suffix + self.extension

    def version_path(self, version_suffix):
        "Path to a version (relative to storage location)"  # FIXME: version_path for version?
        return os.path.join(self.versions_basedir, self.dirname, self.version_name(version_suffix))

    def version_generate(self, version_suffix):
        "Generate a version"  # FIXME: version_generate for version?
        path = self.path
        version_path = self.version_path(version_suffix)
        if not self.site.storage.isfile(version_path):
            version_path = self._generate_version(version_suffix)
        elif self.site.storage.modified_time(path) > self.site.storage.modified_time(version_path):
            version_path = self._generate_version(version_suffix)
        return FileObject(version_path, site=self.site)

    def _generate_version(self, version_suffix):
        """
        Generate Version for an Image.
        value has to be a path relative to the storage location.
        """

        tmpfile = File(tempfile.NamedTemporaryFile())

        try:
            f = self.site.storage.open(self.path)
        except IOError:
            return ""
        im = Image.open(f)
        version_path = self.version_path(version_suffix)
        version_dir, version_basename = os.path.split(version_path)
        root, ext = os.path.splitext(version_basename)
        version = scale_and_crop(im, VERSIONS[version_suffix]['width'], VERSIONS[version_suffix]['height'], VERSIONS[version_suffix]['opts'])
        if not version:
            version = im
        # version methods as defined with VERSIONS
        if 'methods' in VERSIONS[version_suffix].keys():
            for m in VERSIONS[version_suffix]['methods']:
                if callable(m):
                    version = m(version)

        # IF need Convert RGB
        if ext in [".jpg", ".jpeg"] and version.mode not in ("L", "RGB"):
            version = version.convert("RGB")

        # save version
        try:
            version.save(tmpfile, format=Image.EXTENSION[ext.lower()], quality=VERSION_QUALITY, optimize=(os.path.splitext(version_path)[1] != '.gif'))
        except IOError:
            version.save(tmpfile, format=Image.EXTENSION[ext.lower()], quality=VERSION_QUALITY)
        # remove old version, if any
        if version_path != self.site.storage.get_available_name(version_path):
            self.site.storage.delete(version_path)
        self.site.storage.save(version_path, tmpfile)
        # set permissions
        if DEFAULT_PERMISSIONS is not None:
            os.chmod(self.site.storage.path(version_path), DEFAULT_PERMISSIONS)
        return version_path

    # DELETE METHODS
    # delete()
    # delete_versions()
    # delete_admin_versions()

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
