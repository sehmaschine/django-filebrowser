# coding: utf-8

# PYTHON IMPORTS
import re
import os
import unicodedata
import math

# DJANGO IMPORTS
from django.utils import six

# FILEBROWSER IMPORTS
from filebrowser.settings import STRICT_PIL, NORMALIZE_FILENAME, CONVERT_FILENAME

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


def convert_filename(value):
    """
    Convert Filename.
    """

    if NORMALIZE_FILENAME:
        chunks = value.split(os.extsep)
        normalized = []
        for v in chunks:
            v = unicodedata.normalize('NFKD', six.text_type(v)).encode('ascii', 'ignore').decode('ascii')
            v = re.sub(r'[^\w\s-]', '', v).strip()
            normalized.append(v)

        if len(normalized) > 1:
            value = '.'.join(normalized)
        else:
            value = normalized[0]

    if CONVERT_FILENAME:
        value = value.replace(" ", "_").lower()

    return value


def path_strip(path, root):
    if not path or not root:
        return path
    path = os.path.normcase(path)
    root = os.path.normcase(root)
    if path.startswith(root):
        return path[len(root):]
    return path


def scale_and_crop(im, width, height, opts):
    """
    Scale and Crop.
    """

    x, y = [float(v) for v in im.size]

    if 'upscale' not in opts and x < width:
        # version would be bigger than original
        # no need to create this version, because "upscale" isn't defined.
        return False

    if width:
        xr = float(width)
    else:
        xr = float(x*height/y)
    if height:
        yr = float(height)
    else:
        yr = float(y*width/x)

    if 'crop' in opts:
        r = max(xr/x, yr/y)
    else:
        r = min(xr/x, yr/y)

    if r < 1.0 or (r > 1.0 and 'upscale' in opts):
        im = im.resize((int(math.ceil(x*r)), int(math.ceil(y*r))), resample=Image.ANTIALIAS)

    if 'crop' in opts:
        x, y = [float(v) for v in im.size]
        ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
        if ex or ey:
            im = im.crop((int(ex), int(ey), int(ex+xr), int(ey+yr)))
    return im

scale_and_crop.valid_options = ('crop', 'upscale')
