# coding: utf-8

# imports
import os, re, datetime
from time import gmtime, strftime

# django imports
from django.conf import settings

# filebrowser imports
from filebrowser.settings import *
from filebrowser.functions import get_file_type, url_join, is_selectable, get_version_path
from django.utils.encoding import force_unicode

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


class FileObject(object):
    """
    The FileObject represents a File on the Server.
    
    PATH has to be relative to MEDIA_ROOT.
    """
    
    def __init__(self, path):
        self.path = path
        self.url_rel = path.replace("\\","/")
        self.head = os.path.split(path)[0]
        self.filename = os.path.split(path)[1]
        self.filename_lower = self.filename.lower() # important for sorting
        # ABP: fix for dotted folder names
        if os.path.isdir(self.path_full):
           self.filetype = 'Folder'
        else:
            self.filetype = get_file_type(self.filename)
    
    def _filesize(self):
        """
        Filesize.
        """
        path = force_unicode(self.path)
        if os.path.isfile(os.path.join(MEDIA_ROOT, path)) or os.path.isdir(os.path.join(MEDIA_ROOT, path)):
            return os.path.getsize(os.path.join(MEDIA_ROOT, path))
        return ""
    filesize = property(_filesize)
    
    def _date(self):
        """
        Date.
        """
        if os.path.isfile(os.path.join(MEDIA_ROOT, self.path)) or os.path.isdir(os.path.join(MEDIA_ROOT, self.path)):
            return os.path.getmtime(os.path.join(MEDIA_ROOT, self.path))
        return ""
    date = property(_date)
    
    def _datetime(self):
        """
        Datetime Object.
        """
        return datetime.datetime.fromtimestamp(self.date)
    datetime = property(_datetime)
    
    def _extension(self):
        """
        Extension.
        """
        return u"%s" % os.path.splitext(self.filename)[1]
    extension = property(_extension)
    
    def _filetype_checked(self):
        if self.filetype == "Folder" and os.path.isdir(self.path_full):
            return self.filetype
        elif self.filetype != "Folder" and os.path.isfile(self.path_full):
            return self.filetype
        else:
            return ""
    filetype_checked = property(_filetype_checked)
    
    def _path_full(self):
        """
        Full server PATH including MEDIA_ROOT.
        """
        return os.path.join(MEDIA_ROOT, self.path)
    path_full = property(_path_full)
    
    def _path_relative(self):
        return self.path
    path_relative = property(_path_relative)
    
    def _path_relative_directory(self):
        """
        Path relative to initial directory.
        """
        directory_re = re.compile(r'^(%s)' % (DIRECTORY))
        value = directory_re.sub('', self.path)
        return u"%s" % value
    path_relative_directory = property(_path_relative_directory)
    
    def _url_relative(self):
        return self.url_rel
    url_relative = property(_url_relative)
    
    def _url_full(self):
        """
        Full URL including MEDIA_URL.
        """
        return force_unicode(url_join(MEDIA_URL, self.url_rel))
    url_full = property(_url_full)
    
    def _url_save(self):
        """
        URL used for the filebrowsefield.
        """
        if SAVE_FULL_URL:
            return self.url_full
        else:
            return self.url_rel
    url_save = property(_url_save)
    
    def _url_thumbnail(self):
        """
        Thumbnail URL.
        """
        if self.filetype == "Image":
            return u"%s" % url_join(MEDIA_URL, get_version_path(self.path, 'fb_thumb'))
        else:
            return ""
    url_thumbnail = property(_url_thumbnail)
    
    def url_admin(self):
        if self.filetype_checked == "Folder":
            directory_re = re.compile(r'^(%s)' % (DIRECTORY))
            value = directory_re.sub('', self.path)
            return u"%s" % value
        else:
            return u"%s" % url_join(MEDIA_URL, self.path)
    
    def _folder(self):
        directory_re = re.compile(r'^(%s)' % (DIRECTORY.rstrip('/')))
        return u"%s/" % directory_re.sub('', self.head)
    folder = property(_folder)
    
    def _dimensions(self):
        """
        Image Dimensions.
        """
        if self.filetype == 'Image':
            try:
                im = Image.open(os.path.join(MEDIA_ROOT, self.path))
                return im.size
            except:
                pass
        else:
            return False
    dimensions = property(_dimensions)
    
    def _width(self):
        """
        Image Width.
        """
        return self.dimensions[0]
    width = property(_width)
    
    def _height(self):
        """
        Image Height.
        """
        return self.dimensions[1]
    height = property(_height)
    
    def _orientation(self):
        """
        Image Orientation.
        """
        if self.dimensions:
            if self.dimensions[0] >= self.dimensions[1]:
                return "Landscape"
            else:
                return "Portrait"
        else:
            return None
    orientation = property(_orientation)
    
    def _is_empty(self):
        """
        True if Folder is empty, False if not.
        """
        if os.path.isdir(self.path_full):
            if not os.listdir(self.path_full):
                return True
            else:
                return False
        else:
            return None
    is_empty = property(_is_empty)
    
    def __repr__(self):
        return force_unicode(self.url_save)
    
    def __str__(self):
        return force_unicode(self.url_save)
    
    def __unicode__(self):
        return force_unicode(self.url_save)


