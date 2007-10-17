import os

from django.conf import settings

PATH_SERVER = os.path.join(settings.MEDIA_ROOT, 'uploads')
PATH_WWW = settings.MEDIA_URL + 'uploads/'
PATH_ADMIN = '/admin/filebrowser/'
# extensions / lower case (important)
EXTENSIONS = {
    'Folder':[''],
    'Image':['.jpg', '.jpeg', '.gif','.png','.tif','.tiff'],
    'Video':['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    'Document':['.pdf','.doc','.rtf','.txt','.xls','.csv'],
    'Sound':['.mp3','.mp4','.wav','.aiff','.midi'],
    'Code':['.html','.py','.js','.css']
}
# max upload size in bytes
MAX_UPLOAD_SIZE = 2000000
# thumbnail-prefix / thumbnail size
THUMB_PREFIX = 'thumb_'
THUMBNAIL_SIZE = (70, 150)

# WARNING: image-editing is experimental
# NOTE: only ONE of the editing-flags below should be set to true
# use snipshot for basic image-editing
USE_SNIPSHOT = False
# use picnik for advanced image-editing
USE_PICNIK = False
PICNIK_KEY = ""