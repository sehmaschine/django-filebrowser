# coding: utf-8

# imports
import os, unicodedata, re
from time import gmtime, strftime, localtime, mktime, time
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

def url_strip(url, root):
    if not url or not root:
        return url
    if url.startswith(root):
        return url[len(root):]
    return url

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


def sort_by_attr(seq, attr):
    """
    Sort the sequence of objects by object's attribute
    
    Arguments:
    seq  - the list or any sequence (including immutable one) of objects to sort.
    attr - the name of attribute to sort by
    
    Returns:
    the sorted list of objects.
    """
    import operator
    
    # Use the "Schwartzian transform"
    # Create the auxiliary list of tuples where every i-th tuple has form
    # (seq[i].attr, i, seq[i]) and sort it. The second item of tuple is needed not
    # only to provide stable sorting, but mainly to eliminate comparison of objects
    # (which can be expensive or prohibited) in case of equal attribute values.
    intermed = map(None, map(getattr, seq, (attr,)*len(seq)), xrange(len(seq)), seq)
    intermed.sort()
    return map(operator.getitem, intermed, (-1,) * len(intermed))


def url_join(*args):
    """
    URL join routine.
    """
    
    if args[0].startswith("http://"):
        url = "http://"
    elif args[0].startswith("https://"):
        url = "https://"
    else:
        url = "/"
    for arg in args:
        arg = arg.replace("\\", "/")
        arg_split = arg.split("/")
        for elem in arg_split:
            if elem != "" and elem != "http:" and elem != "https:":
                url = url + elem + "/"
    # remove trailing slash for filenames
    if os.path.splitext(args[-1])[1]:
        url = url.rstrip("/")
    return url


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


def get_file_type(filename):
    """
    Get file type as defined in EXTENSIONS.
    """
    
    file_extension = os.path.splitext(filename)[1].lower()
    file_type = ''
    for k,v in EXTENSIONS.iteritems():
        for extension in v:
            if file_extension == extension.lower():
                file_type = k
    return file_type


def get_breadcrumbs(query, path):
    """
    Get breadcrumbs.
    """
    
    breadcrumbs = []
    dir_query = ""
    if path:
        for item in path.split(os.sep):
            dir_query = os.path.join(dir_query,item)
            breadcrumbs.append([item,dir_query])
    return breadcrumbs


def get_filterdate(filterDate, dateTime):
    """
    Get filterdate.
    """
    
    returnvalue = ''
    dateYear = strftime("%Y", gmtime(dateTime))
    dateMonth = strftime("%m", gmtime(dateTime))
    dateDay = strftime("%d", gmtime(dateTime))
    if filterDate == 'today' and int(dateYear) == int(localtime()[0]) and int(dateMonth) == int(localtime()[1]) and int(dateDay) == int(localtime()[2]): returnvalue = 'true'
    elif filterDate == 'thismonth' and dateTime >= time()-2592000: returnvalue = 'true'
    elif filterDate == 'thisyear' and int(dateYear) == int(localtime()[0]): returnvalue = 'true'
    elif filterDate == 'past7days' and dateTime >= time()-604800: returnvalue = 'true'
    elif filterDate == '': returnvalue = 'true'
    return returnvalue


def get_settings_var(directory=DIRECTORY):
    """
    Get settings variables used for FileBrowser listing.
    """
    
    settings_var = {}
    # Main
    settings_var['MEDIA_ROOT'] = MEDIA_ROOT
    settings_var['MEDIA_URL'] = MEDIA_URL
    settings_var['DIRECTORY'] = directory
    # FileBrowser
    settings_var['URL_FILEBROWSER_MEDIA'] = URL_FILEBROWSER_MEDIA
    settings_var['PATH_FILEBROWSER_MEDIA'] = PATH_FILEBROWSER_MEDIA
    # TinyMCE
    settings_var['URL_TINYMCE'] = URL_TINYMCE
    settings_var['PATH_TINYMCE'] = PATH_TINYMCE
    # Extensions/Formats (for FileBrowseField)
    settings_var['EXTENSIONS'] = EXTENSIONS
    settings_var['SELECT_FORMATS'] = SELECT_FORMATS
    # Versions
    settings_var['VERSIONS_BASEDIR'] = VERSIONS_BASEDIR
    settings_var['VERSIONS'] = VERSIONS
    settings_var['ADMIN_VERSIONS'] = ADMIN_VERSIONS
    settings_var['ADMIN_THUMBNAIL'] = ADMIN_THUMBNAIL
    # FileBrowser Options
    settings_var['MAX_UPLOAD_SIZE'] = MAX_UPLOAD_SIZE
    # Normalize Filenames
    settings_var['NORMALIZE_FILENAME'] = NORMALIZE_FILENAME
    # Convert Filenames
    settings_var['CONVERT_FILENAME'] = CONVERT_FILENAME
    # Traverse directories when searching
    settings_var['SEARCH_TRAVERSE'] = SEARCH_TRAVERSE
    return settings_var


def handle_file_upload(path, file, site):
    """
    Handle File Upload.
    """
    
    uploadedfile = None
    try:
        file_path = os.path.join(path, file.name)
        uploadedfile = site.storage.save(file_path, file)
    except Exception, inst:
        raise inst
    return uploadedfile


def is_selectable(filename, selecttype):
    """
    Get select type as defined in FORMATS.
    """
    
    file_extension = os.path.splitext(filename)[1].lower()
    select_types = []
    for k,v in SELECT_FORMATS.iteritems():
        for extension in v:
            if file_extension == extension.lower():
                select_types.append(k)
    return select_types


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


def convert_filename(value):
    """
    Convert Filename.
    """

    if NORMALIZE_FILENAME:
        chunks = value.split(os.extsep)
        normalized = []
        for v in chunks:
            v = unicodedata.normalize('NFKD', unicode(v)).encode('ascii', 'ignore')
            v = re.sub('[^\w\s-]', '', v).strip()
            normalized.append(v)

        if len(normalized) > 1:
            value = '.'.join(normalized)
        else:
            value = normalized[0]

    if CONVERT_FILENAME:
        value = value.replace(" ", "_").lower()

    return value
