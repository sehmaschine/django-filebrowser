# coding: utf-8

# imports
import os, re
from tempfile import NamedTemporaryFile

# django imports
from django.utils.translation import ugettext as _
from django.core.files import File
from django.utils.encoding import smart_unicode

# filebrowser imports
from filebrowser.settings import *

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


def path_strip(path, root):
    if not path or not root:
        return path
    path = os.path.normcase(path)
    root = os.path.normcase(root)
    if path.startswith(root):
        return path[len(root):]
    return path


def get_original_filename(filename):
    filename, ext = os.path.splitext(filename)
    tmp = filename.split("_")
    if tmp[len(tmp)-1] in VERSIONS:
        original_filename = filename.replace("_" + tmp[len(tmp)-1], "") + ext
        return original_filename
    else:
        return None


def get_version_path(value, version_prefix, site=None):
    """
    Construct the path to an image version.
    value has to be a path relative to the storage location.
    
    version_filename = filename + version_prefix + ext
    Returns a relative path to the storage location.
    """
    
    if site.storage.isfile(value):
        path, filename = os.path.split(value)
        relative_path = path_strip(os.path.join(path,''), site.directory)
        filename, ext = os.path.splitext(filename)
        version_filename = filename + "_" + version_prefix + ext
        if VERSIONS_BASEDIR:
            return os.path.join(VERSIONS_BASEDIR, relative_path, version_filename)
        else:
            return os.path.join(site.directory, relative_path, version_filename)
    else:
        return None


def get_original_path(value, site=None):
    """
    Construct the path to an original image based on a version.
    value has to be an path relative to storage location.
    
    Returns a path relative to storage location.
    """
    
    if site.storage.isfile(value):
        path, filename = os.path.split(value)
        if VERSIONS_BASEDIR:
            relative_path = path.replace(VERSIONS_BASEDIR, "")
        else:
            relative_path = path.replace(site.directory, "")
        relative_path = relative_path.lstrip("/")
        original_filename = get_original_filename(filename)
        return os.path.join(site.directory, relative_path, original_filename)
    else:
        return None


def get_path(path, site=None):
    """
    Get path.
    """
    if path.startswith('.') or os.path.isabs(path) or not site.storage.isdir(os.path.join(site.directory, path)):
        return None
    return path


def get_file(path, filename, site=None):
    """
    Get file (or folder).
    """
    converted_path = smart_unicode(os.path.join(site.directory, path, filename))
    if not site.storage.isfile(converted_path) and not site.storage.isdir(converted_path):
        return None
    return filename


def version_generator(value, version_prefix, force=None, site=None):
    """
    Generate Version for an Image.
    value has to be a path relative to the storage location.
    """
    
    # PIL's Error "Suspension not allowed here" work around:
    # s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
    if STRICT_PIL:
        from PIL import ImageFile
    else:
        try:
            from PIL import ImageFile
        except ImportError:
            import ImageFile
    ImageFile.MAXBLOCK = IMAGE_MAXBLOCK # default is 64k
    if not site:
        from filebrowser.sites import site as default_site
        site = default_site
    tmpfile = File(NamedTemporaryFile())

    f = site.storage.open(value)
    im = Image.open(f)
    version_path = get_version_path(value, version_prefix, site=site)
    version_dir, version_basename = os.path.split(version_path)
    root, ext = os.path.splitext(version_basename)
    version = scale_and_crop(im, VERSIONS[version_prefix]['width'], VERSIONS[version_prefix]['height'], VERSIONS[version_prefix]['opts'])
    if not version:
        version = im
    if 'methods' in VERSIONS[version_prefix].keys():
        for m in VERSIONS[version_prefix]['methods']:
            if callable(m):
                version = m(version)
    try:
        version.save(tmpfile, format=Image.EXTENSION[ext.lower()], quality=VERSION_QUALITY, optimize=(os.path.splitext(version_path)[1] != '.gif'))
    except IOError:
        version.save(tmpfile, format=Image.EXTENSION[ext.lower()], quality=VERSION_QUALITY)
    # Remove the old version, if there's any
    if version_path != site.storage.get_available_name(version_path):
        site.storage.delete(version_path)
    site.storage.save(version_path, tmpfile)
    return version_path


def scale_and_crop(im, width, height, opts):
    """
    Scale and Crop.
    """
    
    x, y   = [float(v) for v in im.size]
    
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
        im = im.resize((int(x*r), int(y*r)), resample=Image.ANTIALIAS)
    
    if 'crop' in opts:
        x, y   = [float(v) for v in im.size]
        ex, ey = (x-min(x, xr))/2, (y-min(y, yr))/2
        if ex or ey:
            im = im.crop((int(ex), int(ey), int(x-ex), int(y-ey)))
    return im
    
scale_and_crop.valid_options = ('crop', 'upscale')
