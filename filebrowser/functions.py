# coding: utf-8

# imports
import os
from time import gmtime, strftime, localtime, mktime, time
from tempfile import NamedTemporaryFile

# django imports
from django.utils.translation import ugettext as _
from django.core.files import File
from django.utils.encoding import smart_unicode

# filebrowser imports
from filebrowser.core.functions import *
from filebrowser.settings import *


def get_version_filename(filename, version_prefix):
    filename, ext = os.path.splitext(filename)
    version_filename = filename + "_" + version_prefix + ext
    return version_filename


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
    Construct the PATH to an Image version.
    value has to be a path relative to the location of 
    the site's storage.
    
    version_filename = filename + version_prefix + ext
    Returns a relative path to the location of the site's storage.
    """
    
    if site.storage.isfile(value):
        path, filename = os.path.split(value)
        relative_path = path_strip(path, site.directory)
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
    Construct the PATH to an original Image based on a Image version.
    value has to be an absolute server-path, including MEDIA_ROOT.
    
    Returns an absolute path, including MEDIA_ROOT.
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


def version_generator(value, version_prefix, force=None, site=None):
    """
    Generate Version for an Image.
    value has to be a serverpath relative to MEDIA_ROOT.
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
    
    tmpfile = File(NamedTemporaryFile())
    try:
        f = site.storage.open(value)
        im = Image.open(f)
        version_path = get_version_path(value, version_prefix, site=site)
        version_dir, version_basename = os.path.split(version_path)
        root, ext = os.path.splitext(version_basename)
        version = scale_and_crop(im, VERSIONS[version_prefix]['width'], VERSIONS[version_prefix]['height'], VERSIONS[version_prefix]['opts'])
        if not version:
            version = im
        if 'methods' in VERSIONS[version_prefix].keys():
            for f in VERSIONS[version_prefix]['methods']:
                if callable(f):
                    version = f(version)
        try:
            version.save(tmpfile, format=Image.EXTENSION[ext], quality=VERSION_QUALITY, optimize=(os.path.splitext(version_path)[1].lower() != '.gif'))
        except IOError:
            version.save(tmpfile, format=Image.EXTENSION[ext], quality=VERSION_QUALITY)
        # Remove the old version, if there's any
        if version_path != site.storage.get_available_name(version_path):
            site.storage.delete(version_path)
        site.storage.save(version_path, tmpfile)
        return version_path
    except:
        return None
    finally:
        tmpfile.close()
        f.close()

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
