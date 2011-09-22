# coding: utf-8

##
##
##

from django.utils.translation import ugettext as _
from django.contrib import messages
from django.http import HttpResponseRedirect

from filebrowser.settings import *

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image

def applies_to_all_images(fileobject):
    return fileobject.filetype == 'Image'

def transpose_image(request, fileobjects, operation):
    for fileobject in fileobjects:
        im = Image.open(fileobject.path)
        new_image = im.transpose(operation)
        try:
            new_image.save(fileobject.path, quality=VERSION_QUALITY, optimize=(os.path.splitext(fileobject.path)[1].lower() != '.gif'))
        except IOError:
            new_image.save(fileobject.path, quality=VERSION_QUALITY)
        fileobject.delete_versions()
        messages.add_message(request, messages.SUCCESS, _("Action applied successfully to '%s'" % (fileobject.filename)))


def flip_horizontal(request, fileobjects):
    transpose_image(request, fileobjects, 0)
flip_horizontal.short_description = _(u'Flip horizontal')
flip_horizontal.applies_to = applies_to_all_images

def flip_vertical(request, fileobjects):
    transpose_image(request, fileobjects, 1)
flip_vertical.short_description = _(u'Flip vertical')
flip_vertical.applies_to = applies_to_all_images

def rotate_90_clockwise(request, fileobjects):
    transpose_image(request, fileobjects, 4)
rotate_90_clockwise.short_description = _(u'Rotate 90° CW')
rotate_90_clockwise.applies_to = applies_to_all_images

def rotate_90_counterclockwise(request, fileobjects):
    transpose_image(request, fileobjects, 2)
rotate_90_counterclockwise.short_description = _(u'Rotate 90° CCW')
rotate_90_counterclockwise.applies_to = applies_to_all_images

def rotate_180(request, fileobjects):
    transpose_image(request, fileobjects, 3)
rotate_180.short_description = _(u'Rotate 180°')
rotate_180.applies_to = applies_to_all_images