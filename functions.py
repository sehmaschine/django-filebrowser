
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from time import gmtime, strftime, localtime, mktime, time
from django.core.files import File
import os, re, Image, decimal

# get settings
from filebrowser.fb_settings import *

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
    """
    
    subdir_list = _get_subdir_list(dir_name)
    dir_list = _get_dir_list(dir_name)
    breadcrumbs = ""
    if not query['pop']:
        breadcrumbs = '<a href="%s">%s</a>&nbsp;&rsaquo;&nbsp;' % (URL_HOME,_('Home'))
    breadcrumbs = breadcrumbs + '<a href="%s%s">%s</a>' % (URL_ADMIN, query['query_str_total'], 'FileBrowser')
    if subdir_list:
        for item in subdir_list:
            breadcrumbs = breadcrumbs + '&nbsp;&rsaquo;&nbsp;<a href="%s%s%s">%s</a>' % (URL_ADMIN, item[1], query['query_str_total'], item[0])
    if page:
        if dir_list:
            breadcrumbs = breadcrumbs + '&nbsp;&rsaquo;&nbsp;<a href="%s%s/%s">%s</a>&nbsp;&rsaquo;&nbsp;%s' % (URL_ADMIN, dir_list[1], query['query_str_total'], dir_list[0], _(page))
        else:
            breadcrumbs = breadcrumbs + '&nbsp;&rsaquo;&nbsp;%s' % (_(page))
    elif dir_list:
        breadcrumbs = breadcrumbs + '&nbsp;&rsaquo;&nbsp;%s' % (dir_list[0])
    return mark_safe(breadcrumbs)
    

def _get_sub_query(items, var_1, var_2, var_3):
    """
    Get subquery.
    """
    
    querystring= ''
    for k,v in items:
        if k != var_1 and k != var_2 and k != var_3:
            querystring = querystring + "&" + k + "=" + v
    return querystring
    

def _get_query(request_var):
    """
    Construct query.
    """
    
    query = {}
    if request_var:
        query['query_str_total'] = "?"
        for k,v in request_var.items():
            if k in ['o', 'ot', 'q', 'filter_date', 'filter_type', 'pop']:
                query['query_str_total'] = query['query_str_total'] + "&" + k + "=" + v
        #query['query_str_total'] = "?" + "&".join(["%s=%s" % (k, v) for k, v in request_var.items()])
        query['query_nofilterdate'] = _get_sub_query(request_var.items(), 'filter_date', '', '')
        query['query_nofiltertype'] = _get_sub_query(request_var.items(), 'filter_type', '', '')
        query['query_nosearch'] = _get_sub_query(request_var.items(), 'q', '', '')
        query['query_nosort'] = _get_sub_query(request_var.items(), 'o', 'ot', '')
        query['query_nodelete'] = "?" + _get_sub_query(request_var.items(), 'filename', 'type', '')
        if request_var.get('pop'):
            query['pop'] = "pop=" + request_var.get('pop')
            query['pop_toolbar'] = request_var.get('pop')
        else:
            query['pop'] = ''
            query['pop_toolbar'] = ""
    else:
        query['query_str_total'] = "?"
        query['query_nodelete'] = ""
        query['pop'] = ""
        query['pop_toolbar'] = ""
    query['ot'] = request_var.get('ot', 'desc')
    query['o'] = request_var.get('o', '3')
    query['filter_type'] = request_var.get('filter_type', '')
    query['q'] = request_var.get('q', '')
    query['filter_date'] = request_var.get('filter_date', '')
    if query['ot'] == 'asc':
        query['ot_new'] = 'desc'
    elif query['ot'] == 'desc':
        query['ot_new'] = 'asc'
    return query
    

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
    return returnvalue
    

def _get_filesize(filesize_long):
    """
    Get filesize in a readable format.
    """
    
    filesize_str = ''
    if filesize_long < 1000:
        filesize_str = str(filesize_long) + "&nbsp;B"
    elif filesize_long >= 1000 and filesize_long < 1000000:
        filesize_str = str(filesize_long/1000) + "&nbsp;kB"
    elif filesize_long >= 1000000:
        filesize_str = str(filesize_long/1000000) + "&nbsp;MB"
    return filesize_str
    

def _make_filedict(file_list):
    """
    Make a dict out of the file_list.
        This is for better readability in the templates.
    """
    
    file_dict = []
    for item in file_list:
        temp_list = {}
        temp_list['filename'] = item[0]
        temp_list['filesize_long'] = item[1]
        temp_list['filesize_str'] = item[2]
        temp_list['date'] = item[3]
        temp_list['path_thumb'] = item[4]
        temp_list['link'] = item[5]
        temp_list['select_link'] = item[6]
        temp_list['file_extension'] = item[7]
        temp_list['file_type'] = item[8]
        temp_list['image_dimensions'] = item[9]
        temp_list['thumb_dimensions'] = item[10]
        temp_list['filename_lower'] = item[11]
        temp_list['flag_makethumb'] = item[12]
        temp_list['flag_deletedir'] = item[13]
        file_dict.append(temp_list)
    return file_dict
    

def _get_settings_var(http_post, path):
    """
    Get all settings variables.
    """
    
    settings_var = {}
    settings_var['URL_WWW'] = URL_WWW
    settings_var['URL_ADMIN'] = URL_ADMIN
    settings_var['URL_HOME'] = URL_HOME
    settings_var['PATH_SERVER'] = PATH_SERVER
    settings_var['PATH_FILEBROWSER_MEDIA'] = PATH_FILEBROWSER_MEDIA
    settings_var['PATH_TINYMCE'] = PATH_TINYMCE
    settings_var['EXTENSIONS'] = EXTENSIONS
    settings_var['MAX_UPLOAD_SIZE'] = _get_filesize(MAX_UPLOAD_SIZE)
    settings_var['THUMB_PREFIX'] = THUMB_PREFIX
    settings_var['THUMBNAIL_SIZE'] = THUMBNAIL_SIZE
    settings_var['IMAGE_GENERATOR_LANDSCAPE'] = IMAGE_GENERATOR_LANDSCAPE
    settings_var['IMAGE_GENERATOR_PORTRAIT'] = IMAGE_GENERATOR_PORTRAIT
    settings_var['USE_SNIPSHOT'] = USE_SNIPSHOT
    settings_var['USE_PICNIK'] = USE_PICNIK
    settings_var['PICNIK_KEY'] = PICNIK_KEY
    settings_var['CALLBACK_URL'] = "http://" + http_post + URL_ADMIN + path
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
    if file_extension == "":
        file_extension='unknown'
    file_type = ''
    for k,v in EXTENSIONS.iteritems():
        for extension in v:
            if file_extension == extension.lower():
                file_type = k
    return file_type
    

def _make_image_thumbnail(PATH_SERVER, path, filename):
    """
    Make Thumbnail for an Image.
    """
    
    file_path = os.path.join(PATH_SERVER, path, filename)
    thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + filename)
    msg = ""
    try:
        im = Image.open(file_path)
        im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        im.save(thumb_path)
    except IOError:
        msg = "%s: %s" % (file.name, _('Thumbnail creation failed.'))
    return msg
    

def _image_generator(PATH_SERVER, path, filename):
    """
    Generate Versions for an Image.
    """
    
    file_path = os.path.join(PATH_SERVER, path, filename)
    versions_path = os.path.join(PATH_SERVER, path, filename.replace(".", "_").lower() + "_versions")
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
                new_image.save(image_path, quality=90, optimize=1)
                # MAKE THUMBNAIL
                _make_image_thumbnail(PATH_SERVER, os.path.join(path, filename.replace(".", "_").lower() + "_versions"), prefix[0] + filename)
        except IOError:
            msg = "%s: %s" % (filename, _('Image creation failed.'))
    return msg
    

def _image_crop_generator(PATH_SERVER, path, filename):
    """
    Generate Cropped Versions for an Image.
    """
    
    file_path = os.path.join(PATH_SERVER, path, filename)
    versions_path = os.path.join(PATH_SERVER, path, filename.replace(".", "_").lower() + "_versions")
    if not os.path.isdir(versions_path):
        os.mkdir(versions_path)
        os.chmod(versions_path, 0775)
    im = Image.open(file_path)
    dimensions = im.size
    current_width = dimensions[0]
    current_height = dimensions[1]
    msg = ""
    for prefix in IMAGE_CROP_GENERATOR:
        image_path = os.path.join(versions_path, prefix[0] + filename)
        try:
            # DIMENSIONS
            dimensions = im.size
            current_width = dimensions[0]
            current_height = dimensions[1]
            ratio = decimal.Decimal(0)
            ratio = decimal.Decimal(current_width)/decimal.Decimal(current_height)
            # new_size
            # either side of the img must be at least the crop_size_width
            new_size_width = prefix[1]
            new_size_height = int(new_size_width/ratio)
            if new_size_width > new_size_height:
                new_size_height = new_size_width
                new_size_width = int(new_size_height*ratio) 
            new_size = (new_size_width, new_size_height)                        
            # crop_size
            # trying to crop the middle of the img
            crop_size_width = prefix[1]
            if prefix[2]:
                crop_size_height = prefix[2]
            else:
                crop_size_height = crop_size_width
            upper_left_x = int((new_size_width-crop_size_width)/2)
            upper_left_y = int((new_size_height-crop_size_height)/2)
            crop_size = (upper_left_x, upper_left_y, upper_left_x+crop_size_width, upper_left_y+crop_size_height)
            # NEW IMAGE
            im = Image.open(file_path)
            # resize img first
            new_image = im.resize(new_size, Image.ANTIALIAS)
            # then crop
            cropped_image = new_image.crop(crop_size)
            cropped_image.save(image_path, quality=90, optimize=1)
            # MAKE THUMBNAIL
            _make_image_thumbnail(PATH_SERVER, os.path.join(path, filename.replace(".", "_").lower() + "_versions"), prefix[0] + filename)
        except IOError:
            msg = "%s: %s" % (filename, _('Image creation failed.'))
    return msg
    
    

