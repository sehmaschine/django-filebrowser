# coding: utf-8

# imports
import os

# django imports
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# settings for django-tinymce
try:
    import tinymce.settings
    DEFAULT_URL_TINYMCE = tinymce.settings.JS_BASE_URL + '/'
    DEFAULT_PATH_TINYMCE = tinymce.settings.JS_ROOT + '/'
except ImportError:
    DEFAULT_URL_TINYMCE = settings.ADMIN_MEDIA_PREFIX + "tinymce/jscripts/tiny_mce/"
    DEFAULT_PATH_TINYMCE = os.path.join(settings.STATIC_ROOT, 'admin/tinymce/jscripts/tiny_mce/')

# PATH AND URL SETTINGS
# Main Media Settings
MEDIA_ROOT = getattr(settings, "FILEBROWSER_MEDIA_ROOT", settings.MEDIA_ROOT)
MEDIA_URL = getattr(settings, "FILEBROWSER_MEDIA_URL", settings.MEDIA_URL)
# Main FileBrowser Directory. This has to be a directory within MEDIA_ROOT.
# Leave empty in order to browse all files under MEDIA_ROOT.
# DO NOT USE A SLASH AT THE BEGINNING, DO NOT FORGET THE TRAILING SLASH AT THE END.
DIRECTORY = getattr(settings, "FILEBROWSER_DIRECTORY", 'uploads/')
# The URL/PATH to your filebrowser media-files.
URL_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_URL_FILEBROWSER_MEDIA", os.path.join(settings.STATIC_URL, 'filebrowser/'))
PATH_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_PATH_FILEBROWSER_MEDIA", os.path.join(settings.STATIC_ROOT, 'filebrowser/'))
# The URL/PATH to your TinyMCE Installation.
URL_TINYMCE = getattr(settings, "FILEBROWSER_URL_TINYMCE", DEFAULT_URL_TINYMCE)
PATH_TINYMCE = getattr(settings, "FILEBROWSER_PATH_TINYMCE", DEFAULT_PATH_TINYMCE)

# EXTENSIONS AND FORMATS
# Allowed Extensions for File Upload. Lower case is important.
EXTENSIONS = getattr(settings, "FILEBROWSER_EXTENSIONS", {
    'Folder': [''],
    'Image': ['.jpg','.jpeg','.gif','.png','.tif','.tiff'],
    'Document': ['.pdf','.doc','.rtf','.txt','.xls','.csv'],
    'Video': ['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    'Audio': ['.mp3','.mp4','.wav','.aiff','.midi','.m4p']
})
# Define different formats for allowed selections.
# This has to be a subset of EXTENSIONS.
# e.g., add ?type=image to the browse-URL ...
SELECT_FORMATS = getattr(settings, "FILEBROWSER_SELECT_FORMATS", {
    'file': ['Folder','Image','Document','Video','Audio'],
    'image': ['Image'],
    'document': ['Document'],
    'media': ['Video','Audio'],
})

# EXTRA SETTINGS
# If set to True, the FileBrowser will not try to import a mis-installed PIL.
STRICT_PIL = getattr(settings, 'FILEBROWSER_STRICT_PIL', False)
# Exclude files matching any of the following regular expressions
# Default is to exclude 'thumbnail' style naming of image-thumbnails.
EXTENSION_LIST = []
for exts in EXTENSIONS.values():
    EXTENSION_LIST += exts
EXCLUDE = getattr(settings, 'FILEBROWSER_EXCLUDE', '')
# Max. Upload Size in Bytes.
MAX_UPLOAD_SIZE = getattr(settings, "FILEBROWSER_MAX_UPLOAD_SIZE", 10485760)
# Convert Filename (replace spaces and convert to lowercase)
CONVERT_FILENAME = getattr(settings, "FILEBROWSER_CONVERT_FILENAME", True)
# Max. Entries per Page
# Loading a Sever-Directory with lots of files might take a while
# Use this setting to limit the items shown
LIST_PER_PAGE = getattr(settings, "FILEBROWSER_LIST_PER_PAGE", 50)
# Default Sorting
# Options: date, filesize, filename_lower, filetype_checked
DEFAULT_SORTING_BY = getattr(settings, "FILEBROWSER_DEFAULT_SORTING_BY", "date")
# Sorting Order: asc, desc
DEFAULT_SORTING_ORDER = getattr(settings, "FILEBROWSER_DEFAULT_SORTING_ORDER", "desc")
# regex to clean dir names before creation
FOLDER_REGEX = getattr(settings, "FILEBROWSER_FOLDER_REGEX", r'^[\w._/-]+$')
# Traverse directories when searching
SEARCH_TRAVERSE = getattr(settings, "FILEBROWSER_SEARCH_TRAVERSE", False)
# Default Upload and Version Permissions
DEFAULT_PERMISSIONS = getattr(settings, "FILEBROWSER_DEFAULT_PERMISSIONS", 0755)

# EXTRA TRANSLATION STRINGS
# The following strings are not availabe within views or templates
_('Folder')
_('Image')
_('Video')
_('Document')
_('Audio')
