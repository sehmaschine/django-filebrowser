# coding: utf-8

from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from time import gmtime, strftime, localtime, mktime, time
from django.core.files import File
import os, re, decimal

# get settings
from filebrowser.fb_settings import *

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


def _sort_by_attr(seq, attr):
    """Sort the sequence of objects by object's attribute
    
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
    

def _url_join(*args):
    url = "/"
    for arg in args:
        arg_split = arg.split("/")
        for elem in arg_split:
            if elem != "":
                url = url + elem + "/"
    return url
    

def _get_path(dir_name):
    """
    Get path.
    """
    
    if dir_name:
        path = dir_name + "/"
    else:
        path = ""
    return path
    

def _get_subdir_list(dir_name):
    """
    Get a list of subdirectories.
    """
    
    subdir_list = []
    if dir_name:
        dirlink = ''
        dir_items = dir_name.split('/')
        dir_items.pop()
        for dirname in dir_items:
            dirlink = dirlink + dirname + '/'
            subdir_list.append([dirname,dirlink])
    return subdir_list
    

def _get_dir_list(dir_name):
    """
    Get a list of directories.
    """
    
    dir_list = []
    if dir_name:
        dir_items = dir_name.split('/')
        dirname = dir_items.pop()
        dir_list.append(dirname)
        dir_list.append(dir_name)
    return dir_list
    

def _get_breadcrumbs(query, dir_name, page):
    """
    Get breadcrumbs.
        Format: [Name,Link,AddQueryString]
    """
    
    subdir_list = _get_subdir_list(dir_name)
    dir_list = _get_dir_list(dir_name)
    
    breadcrumbs = []
    if not query.get('pop'):
        breadcrumbs.append([_('Home'),URL_HOME,False])
    breadcrumbs.append([_('FileBrowser'),URL_ADMIN,True])
    if subdir_list:
        for item in subdir_list:
            breadcrumbs.append([item[0],_url_join(URL_ADMIN, item[1]),True])
    if page:
        if dir_list:
            breadcrumbs.append([dir_list[0],_url_join(URL_ADMIN, dir_list[1]),True])
            breadcrumbs.append([page,"",False])
        else:
            breadcrumbs.append([page,"",False])
    elif dir_list:
        breadcrumbs.append([dir_list[0],"",False])
    return breadcrumbs
    

def _get_filterdate(filterDate, dateTime):
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
    

def _get_settings_var():
    """
    Get all settings variables.
    """
    
    settings_var = {}
    settings_var['URL_WWW'] = URL_WWW
    settings_var['URL_ADMIN'] = URL_ADMIN
    settings_var['URL_HOME'] = URL_HOME
    settings_var['URL_FILEBROWSER_MEDIA'] = URL_FILEBROWSER_MEDIA
    settings_var['URL_TINYMCE'] = URL_TINYMCE
    settings_var['PATH_SERVER'] = PATH_SERVER
    #settings_var['PATH_FILEBROWSER_MEDIA'] = PATH_FILEBROWSER_MEDIA
    settings_var['PATH_TINYMCE'] = PATH_TINYMCE
    settings_var['EXTENSIONS'] = EXTENSIONS
    settings_var['MAX_UPLOAD_SIZE'] = MAX_UPLOAD_SIZE
    settings_var['IMAGE_MAXBLOCK'] = IMAGE_MAXBLOCK
    settings_var['THUMB_PREFIX'] = THUMB_PREFIX
    settings_var['THUMBNAIL_SIZE'] = THUMBNAIL_SIZE
    settings_var['USE_IMAGE_GENERATOR'] = USE_IMAGE_GENERATOR
    settings_var['IMAGE_GENERATOR_DIRECTORY'] = IMAGE_GENERATOR_DIRECTORY
    settings_var['IMAGE_GENERATOR_LANDSCAPE'] = IMAGE_GENERATOR_LANDSCAPE
    settings_var['IMAGE_GENERATOR_PORTRAIT'] = IMAGE_GENERATOR_PORTRAIT
    settings_var['FORCE_GENERATOR'] = FORCE_GENERATOR
    return settings_var
    
    
def _handle_file_upload(PATH_SERVER, path, file):
    """
    Handle File Upload.
    """
    
    file_path = os.path.join(PATH_SERVER, path, file.name)
    destination = open(file_path, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    

def _get_file_type(filename):
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
    

def _is_selectable(filename, selecttype):
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
    

def _image_generator(PATH_SERVER, path, filename):
    """
    Generate Versions for an Image.
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
    
    file_path = os.path.join(PATH_SERVER, path, filename)
    versions_path = os.path.join(PATH_SERVER, path, filename.replace(".", "_").lower() + IMAGE_GENERATOR_DIRECTORY)
    if not os.path.isdir(versions_path):
        os.mkdir(versions_path)
        os.chmod(versions_path, 0775)
    im = Image.open(file_path)
    dimensions = im.size
    current_width = dimensions[0]
    current_height = dimensions[1]
    msg = ""
    if int(current_width) > int(current_height):
        generator_to_use = IMAGE_GENERATOR_LANDSCAPE
    else:
        generator_to_use = IMAGE_GENERATOR_PORTRAIT
    for prefix in generator_to_use: 
        image_path = os.path.join(versions_path, prefix[0] + filename)
        try:
            # DIMENSIONS
            ratio = decimal.Decimal(0)
            ratio = decimal.Decimal(current_width)/decimal.Decimal(current_height)
            new_size_width = prefix[1]
            new_size_height = int(new_size_width/ratio)
            new_size = (new_size_width, new_size_height)
            # ONLY MAKE NEW IMAGE VERSION OF ORIGINAL IMAGE IS BIGGER THAN THE NEW VERSION
            # OTHERWISE FAIL SILENTLY
            if int(current_width) > int(new_size_width):
                # NEW IMAGE
                new_image = im.resize(new_size, Image.ANTIALIAS)
                if im.format == 'GIF':
                    try:
                        transparency = im.info['transparency'] 
                    except KeyError:
                        new_image.save(image_path)
                    else:
                        new_image.save(image_path, transparency=transparency)
                else:
                    try:
                        new_image.save(image_path, quality=90, optimize=1)
                    except IOError:
                        new_image.save(image_path)
            elif FORCE_GENERATOR_RUN:
                im.save(image_path)
        except IOError:
            msg = "%s: %s" % (filename, _('Image creation failed.'))
    return msg
    

def scale_and_crop(im, requested_size, opts):
    x, y   = [float(v) for v in im.size]
    xr, yr = [float(v) for v in requested_size]
    
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
    

def _image_crop_generator(PATH_SERVER, path, filename):
    """
    Generate Cropped Versions for an Image.
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
    
    file_path = os.path.join(PATH_SERVER, path, filename)
    versions_path = os.path.join(PATH_SERVER, path, filename.replace(".", "_").lower() + IMAGE_GENERATOR_DIRECTORY)
    if not os.path.isdir(versions_path):
        os.mkdir(versions_path)
        os.chmod(versions_path, 0775)
    im = Image.open(file_path)
    msg = ""
    for prefix in IMAGE_CROP_GENERATOR:
        image_path = os.path.join(versions_path, prefix[0] + filename)
        try:
            cropped_image = scale_and_crop(im, (prefix[1], prefix[2]), ['crop'])
            cropped_image.save(image_path, quality=90, optimize=1)
        except IOError:
            msg = "%s: %s" % (filename, _('Image creation failed.'))
    return msg
    

def _is_image_version(file):
    image_version = False
    for item in IMAGE_GENERATOR_LANDSCAPE:
        if file.startswith(item[0]):
            image_version = True
    for item in IMAGE_GENERATOR_PORTRAIT:
        if file.startswith(item[0]):
            image_version = True
    for item in IMAGE_CROP_GENERATOR:
        if file.startswith(item[0]):
            image_version = True
    return image_version
    

