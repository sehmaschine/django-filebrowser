# coding: utf-8

import os
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# settings for django-tinymce
try:
    import tinymce.settings
    DEFAULT_URL_TINYMCE = tinymce.settings.JS_BASE_URL + '/'
    DEFAULT_PATH_TINYMCE = tinymce.settings.JS_ROOT + '/'
except ImportError:
    DEFAULT_URL_TINYMCE = settings.ADMIN_MEDIA_PREFIX + "tinymce/jscripts/tiny_mce/"
    DEFAULT_PATH_TINYMCE = os.path.join(settings.MEDIA_ROOT, 'admin/tinymce/jscripts/tiny_mce/')

# The location of your media-files.
# This is the base URL for all your media-files accessible for the FileBrowser.
# Note: When you set URL_WWW to settings.MEDIA_URL you can use all your media-files with the FileBrowser.
# Nevertheless, you may want to limit this to a subdirectory of settings.MEDIA_URL or a seperate media-server.
# Important: If you change this setting, you should also change PATH_SERVER.
URL_WWW = getattr(settings, "FILEBROWSER_URL_WWW", '/media/uploads/')

# The FileBrowser Admin-URL.
# Note: If you change this URL, you also have to change the file urls.py.
URL_ADMIN = getattr(settings, "FILEBROWSER_URL_ADMIN", '/admin/filebrowser/')

# The URL to your Admin Index-Site.
URL_HOME = getattr(settings, "FILEBROWSER_URL_HOME", '/admin/')

# The URL to your filebrowser media-files.
# Note: You have to change this setting, if you install the media-files of the FileBrowser outside
# your admin-media directory.
URL_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_URL_FILEBROWSER_MEDIA", settings.ADMIN_MEDIA_PREFIX + "filebrowser/")

# The URL to your TinyMCE Installation.
# Note: You have to change this setting, if you install TinyMCE outside your admin-media directory.
URL_TINYMCE = getattr(settings, "FILEBROWSER_URL_TINYMCE", DEFAULT_URL_TINYMCE)

# Save full domain-relative URLs to your model fields,
# or False (default) to save paths relative to settings.MEDIA_URL.
# Used in conjunction with the FileBrowseField.
SAVE_FULL_URL = getattr(settings, "FILEBROWSER_SAVE_FULL_URL", True)

# The server-path to media-files. This is the initial/root server-path for the FileBrowser.
# Important: If you change this setting, you should also change URL_WWW.
PATH_SERVER = getattr(settings, "FILEBROWSER_PATH_SERVER", os.path.join(settings.MEDIA_ROOT, 'uploads'))

# The server-path to your filebrowser media-files.
# Note: You have to change this setting, if you install the media-files of the FileBrowser outside
# your admin-media directory. 
PATH_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_PATH_FILEBROWSER_MEDIA", os.path.join(settings.MEDIA_ROOT, 'admin/filebrowser/'))

# The server-path to your TinyMCE Installation.
# Note: You have to change this setting, if you install TinyMCE outside your admin-media directory.
PATH_TINYMCE = getattr(settings, "FILEBROWSER_PATH_TINYMCE", DEFAULT_PATH_TINYMCE)

# Allowed Extensions for File Upload. Lower case is important.
# Please be aware that there are Icons for the default extension settings.
# Therefore, if you add a category (e.g. "Misc"), you won't get an icon.
EXTENSIONS = getattr(settings, "FILEBROWSER_EXTENSIONS", {
    'Folder':[''],
    'Image':['.jpg', '.jpeg', '.gif','.png','.tif','.tiff'],
    'Video':['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    'Document':['.pdf','.doc','.rtf','.txt','.xls','.csv'],
    'Sound':['.mp3','.mp4','.wav','.aiff','.midi'],
    'Code':['.html','.py','.js','.css']
})
# Define different formats for allowed selections.
# This has to be a subset of EXTENSIONS
SELECT_FORMATS = getattr(settings, "FILEBROWSER_SELECT_FORMATS", {
    'File':['Folder','Document'],
    'Image':['Image'],
    'Media':['Video','Sound']
})

# Max. Upload Size in Bytes.
MAX_UPLOAD_SIZE = getattr(settings, "FILEBROWSER_MAX_UPLOAD_SIZE", 5000000)

# PIL's Error "Suspension not allowed here" work around:
# s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
IMAGE_MAXBLOCK = getattr(settings, 'FILEBROWSER_IMAGE_MAXBLOCK', 1024*1024)

# Exclude files matching any of the following regular expressions
# Default is to exclude 'sorl-thumbnail' style naming of jpg, png, or gif thumbnails
EXCLUDE = (r'_(jpg|png|gif)_.*_q\d{1,3}\.(jpg|png|gif)', )

# The prefix for your thumbnails.
# If you have an Image "myimage.jpg", your thumbnail will be "thumb_myimage.jpg" by default.
THUMB_PREFIX = getattr(settings, 'FILEBROWSER_THUMB_PREFIX', 'thumb_')

# The size of your thumbnails for the Admin-Interface.
# Note: This Thumbnail is for diplaying your Image within the Admin-Interface.
# Because of the low quality, it´s not intended to use this Thumbnail on your Website.
# For displaying Thumbnails on a Website, use "Image Generator" instead.
THUMBNAIL_SIZE = getattr(settings, 'FILEBROWSER_THUMBNAIL_SIZE', '50x50')

# Whether or not to use the ImageGenerator.
# When this is True, you´ll get a checkbox called "Use Image Generator" with every Upload-Field.
# Moreover, every Image will have a button "Generate Images" to generate Image versions
# (this is useful, if Images are uploaded using FTP and not the FileBrowser -
# you can upload Images using FTP and generate the Image Versions afterwards). 
USE_IMAGE_GENERATOR = getattr(settings, 'FILEBROWSER_USE_IMAGE_GENERATOR', True)

# The postfix for your "Image Versions"-directory.
# If you Upload an Image called "myimage.jpg", your versions-directory will be called
# "myimage_jpg_versions" by default. 
IMAGE_GENERATOR_DIRECTORY = getattr(settings, 'FILEBROWSER_IMAGE_GENERATOR_DIRECTORY', '_versions')

# A list of Images to generate in the format (prefix, image width).
IMAGE_GENERATOR_LANDSCAPE = getattr(settings, "FILEBROWSER_IMAGE_GENERATOR_LANDSCAPE", [('thumbnail_',140),('small_',300),('medium_',460),('big_',620)])

# A list of Images to generate in the format (prefix, image width).
IMAGE_GENERATOR_PORTRAIT = getattr(settings, "FILEBROWSER_IMAGE_GENERATOR_PORTRAIT", [('thumbnail_',140),('small_',300),('medium_',460),('big_',620)])

# A list of Images to generate in the format (prefix, image width, image height). 
IMAGE_CROP_GENERATOR = getattr(settings, "FILEBROWSER_IMAGE_CROP_GENERATOR", [('cropped_',60,60),('croppedthumbnail_',140,140)])

# When accessing FilebrowserField.landscape.xxx FilebrowserField.portrait.xxx, check if
# the file actually exists /// Set to True to always check
CHECK_EXISTS = getattr(settings, 'FILEBROWSER_CHECK_EXISTS', True)

# Force the use of the image generator each time a file is uploaded via FileBrowser
FORCE_GENERATOR = getattr(settings, 'FILEBROWSER_FORCE_GENERATOR', False)

# If set True, Image Generator will copy the image if the dimensions are smaller than the
# specified dimensions.
FORCE_GENERATOR_RUN = getattr(settings, 'FILEBROWSER_FORCE_GENERATOR_RUN', False)

# if set True, then FileBrowser will not try to import a mis-installed PIL
STRICT_PIL = getattr(settings, 'FILEBROWSER_STRICT_PIL', False)

# list of names not allowed for folders
DISALLOWED_FOLDER_NAMES = getattr(settings, "FILEBROWSER_DISALLOWED_FOLDER_NAMES", ['mkdir', 'upload', 'rename', 'delete'])

