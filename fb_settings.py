import os
from django.conf import settings

# your media-url
URL_WWW = settings.MEDIA_URL + 'uploads/'
# your filebrowser admin url
URL_ADMIN = getattr(settings, "FILEBROWSER_URL_ADMIN", '/admin/filebrowser/')

# paths
PATH_SERVER = os.path.join(settings.MEDIA_ROOT, 'uploads')
# path to your filebrowser media (img/js/css)
PATH_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_PATH_MEDIA", "/media/admin/filebrowser/")
# path to tinymce
PATH_TINYMCE = getattr(settings, "FILEBROWSER_PATH_TINYMCE", "/media/admin/tinymce/jscripts/tiny_mce/")

# extensions / lower case (important)
EXTENSIONS = getattr(settings, "FILEBROWSER_EXTENSIONS", {
    'Folder':[''],
    'Image':['.jpg', '.jpeg', '.gif','.png','.tif','.tiff'],
    'Video':['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    'Document':['.pdf','.doc','.rtf','.txt','.xls','.csv'],
    'Sound':['.mp3','.mp4','.wav','.aiff','.midi'],
    'Code':['.html','.py','.js','.css']
})

# max upload size in bytes
MAX_UPLOAD_SIZE = getattr(settings, "FILEBROWSER_MAX_UPLOAD_SIZE", 2000000)

# thumbnail-prefix / thumbnail size
THUMB_PREFIX = getattr(settings, 'FILEBROWSER_THUMB_PREFIX', 'thumb_')
THUMBNAIL_SIZE = getattr(settings, 'FILEBROWSER_THUMBNAIL_SIZE', (70, 150))

# image generator (thumb, new image width)
# if you do not need to save different image sizes
# write IMAGE_GENERATOR = ""
IMAGE_GENERATOR = getattr(settings, "FILEBROWSER_IMAGE_GENERATOR", [('small_',140),('medium_',300),('big_',620)])

# WARNING: image-editing is experimental
# NOTE: only ONE of the editing-flags below should be set to true
# use snipshot for basic image-editing
USE_SNIPSHOT = getattr(settings, "FILEBROWSER_USE_SNIPSHOT", False)
# use picnik for advanced image-editing
USE_PICNIK = getattr(settings, "FILEBROWSER_USE_PICNIK", False)
PICNIK_KEY = getattr(settings, "FILEBROWSER_PICNIK_KEY", "")