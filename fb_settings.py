import os
from django.conf import settings

# your media-url
URL_WWW = settings.MEDIA_URL + 'uploads/'
# your filebrowser admin url
URL_ADMIN = getattr(settings, "FILEBROWSER_URL_ADMIN", '/admin/filebrowser/')
# home url
URL_HOME = getattr(settings, "FILEBROWSER_URL_HOME", '/admin/')

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
MAX_UPLOAD_SIZE = getattr(settings, "FILEBROWSER_MAX_UPLOAD_SIZE", 5000000)

# thumbnail-prefix / thumbnail size
THUMB_PREFIX = getattr(settings, 'FILEBROWSER_THUMB_PREFIX', 'thumb_')
THUMBNAIL_SIZE = getattr(settings, 'FILEBROWSER_THUMBNAIL_SIZE', (50, 150))

# image generator (prefix, new image width)
# if you do not need to save different image sizes
# write IMAGE_GENERATOR = ""
IMAGE_GENERATOR_LANDSCAPE = getattr(settings, "FILEBROWSER_IMAGE_GENERATOR_LANDSCAPE", [('thumbnail_',134),('small_',294),('medium_',454),('big_',614)])
IMAGE_GENERATOR_PORTRAIT = getattr(settings, "FILEBROWSER_IMAGE_GENERATOR_PORTRAIT", [('thumbnail_',134),('small_',294),('medium_',454),('big_',614)])
# generator for a cropped image (prefix, width)
# if you do not need to save different image sizes
# write IMAGE_GENERATOR = ""
IMAGE_CROP_GENERATOR = getattr(settings, "FILEBROWSER_IMAGE_CROP_GENERATOR", [('cropped_',54,54),('croppedthumbnail_',134,134)])