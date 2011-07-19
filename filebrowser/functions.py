# coding: utf-8

# imports
import os, re, decimal
from time import gmtime, strftime, localtime, mktime, time
from urlparse import urlparse

# django imports
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import smart_str

# filebrowser imports
from filebrowser.settings import *
filebrowser_storage = FileSystemStorage(location=MEDIA_ROOT)

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


def url_to_path(value):
    """
    Change URL to PATH.
    value has to be an URL relative to MEDIA URL or a full URL (including MEDIA_URL).
    
    Returns an absolute server-path, including MEDIA_ROOT.
    """
    
    mediaurl_re = re.compile(r'^(%s)' % (MEDIA_URL))
    value = mediaurl_re.sub('', value)
    return os.path.join(MEDIA_ROOT, value)


def path_to_url(value):
    """
    Change PATH to URL.
    value has to be an absolute server-path, including MEDIA_ROOT.
    
    Return an URL including MEDIA_URL.
    """
    
    mediaurl_re = re.compile(r'^(%s)' % (MEDIA_ROOT))
    value = mediaurl_re.sub('', value)
    return url_join(MEDIA_URL, value)


def dir_from_url(value):
    """
    Get the relative server directory from a URL.
    URL has to be an absolute URL including MEDIA_URL or
    an URL relative to MEDIA_URL.
    """
    
    mediaurl_re = re.compile(r'^(%s)' % (MEDIA_URL))
    value = mediaurl_re.sub('', value)
    directory_re = re.compile(r'^(%s)' % (DIRECTORY))
    value = directory_re.sub('', value)
    return os.path.split(value)[0]


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


def get_version_path(value, version_prefix):
    """
    Construct the PATH to an Image version.
    value has to be an absolute server-path, including MEDIA_ROOT.
    
    version_filename = filename + version_prefix + ext
    Returns an absolute path, including MEDIA_ROOT.
    """
    
    if os.path.isfile(value):
        path, filename = os.path.split(value)
        relative_path = path.replace(os.path.join(MEDIA_ROOT,DIRECTORY), "")
        filename, ext = os.path.splitext(filename)
        version_filename = filename + "_" + version_prefix + ext
        if VERSIONS_BASEDIR:
            return os.path.join(MEDIA_ROOT, VERSIONS_BASEDIR, relative_path, version_filename)
        else:
            return os.path.join(MEDIA_ROOT, DIRECTORY, relative_path, version_filename)
    else:
        return None


def get_original_path(value):
    """
    Construct the PATH to an original Image based on a Image version.
    value has to be an absolute server-path, including MEDIA_ROOT.
    
    Returns an absolute path, including MEDIA_ROOT.
    """
    
    if os.path.isfile(value):
        path, filename = os.path.split(value)
        if VERSIONS_BASEDIR:
            relative_path = path.replace(os.path.join(MEDIA_ROOT,VERSIONS_BASEDIR), "")
        else:
            relative_path = path.replace(os.path.join(MEDIA_ROOT,DIRECTORY), "")
        relative_path = relative_path.lstrip("/")
        original_filename = get_original_filename(filename)
        return os.path.join(MEDIA_ROOT, DIRECTORY, relative_path, original_filename)
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
    else:
        url = "/"
    for arg in args:
        arg = arg.replace("\\", "/")
        arg_split = arg.split("/")
        for elem in arg_split:
            if elem != "" and elem != "http:":
                url = url + elem + "/"
    # remove trailing slash for filenames
    if os.path.splitext(args[-1])[1]:
        url = url.rstrip("/")
    return url


def get_path(path):
    """
    Get path.
    """
    if path.startswith('.') or os.path.isabs(path) or not os.path.isdir(os.path.join(MEDIA_ROOT, DIRECTORY, path)):
        return None
    return path


def get_file(path, filename):
    """
    Get file (or folder).
    """
    converted_path = smart_str(os.path.join(MEDIA_ROOT, DIRECTORY, path, filename))
    if not os.path.isfile(converted_path) and not os.path.isdir(converted_path):
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


def get_settings_var():
    """
    Get settings variables used for FileBrowser listing.
    """
    
    settings_var = {}
    # Main
    settings_var['MEDIA_ROOT'] = MEDIA_ROOT
    settings_var['MEDIA_URL'] = MEDIA_URL
    settings_var['DIRECTORY'] = DIRECTORY
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
    # Convert Filenames
    settings_var['CONVERT_FILENAME'] = CONVERT_FILENAME
    # Traverse directories when searching
    settings_var['SEARCH_TRAVERSE'] = SEARCH_TRAVERSE
    return settings_var


def handle_file_upload(path, file):
    """
    Handle File Upload.
    """
    
    uploadedfile = None
    try:
        file_path = os.path.join(path, file.name)
        uploadedfile = filebrowser_storage.save(file_path, file)
        os.chmod(uploadedfile, FB_DEFAULT_PERMISSIONS)
    except Exception, inst:
        print "___filebrowser.functions.handle_file_upload(): could not save uploaded file"
        print "ERROR: ", inst
        print "___"
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


def version_generator(value, version_prefix, force=None):
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
    
    try:
        im = Image.open(smart_str(os.path.join(MEDIA_ROOT, value)))
        version_path = get_version_path(value, version_prefix)
        version_dir = os.path.split(version_path)[0]
        if not os.path.isdir(version_dir):
            os.makedirs(version_dir)
            os.chmod(version_dir, FB_DEFAULT_PERMISSIONS)
        version = scale_and_crop(im, VERSIONS[version_prefix]['width'], VERSIONS[version_prefix]['height'], VERSIONS[version_prefix]['opts'])
        if version:
            try:
                version.save(version_path, quality=VERSION_QUALITY, optimize=(os.path.splitext(version_path)[1].lower() != '.gif'))
            except IOError:
                version.save(version_path, quality=VERSION_QUALITY)
        else:
            # version wasn't created
            # save the original image with the versions name
            try:
                im.save(version_path, quality=VERSION_QUALITY, optimize=(os.path.splitext(version_path)[1].lower() != '.gif'))
            except IOError:
                im.save(version_path, quality=VERSION_QUALITY)
        return version_path
    except:
        return None


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
    
    if CONVERT_FILENAME:
        return value.replace(" ", "_").lower()
    else:
        return value


