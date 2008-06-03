from django.shortcuts import render_to_response
from django.template import RequestContext as Context
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from time import gmtime, strftime, localtime, mktime, time
import os, string, ftplib, re, Image, decimal

# get settings
from filebrowser.fb_settings import *

def _get_path(dir_name):
    if dir_name:
        path = dir_name + "/"
    else:
        path = ""
    return path
    
def _get_subdir_list(dir_name):
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
    dir_list = []
    if dir_name:
        dir_items = dir_name.split('/')
        dirname = dir_items.pop()
        dir_list.append(dirname)
        dir_list.append(dir_name)
    return dir_list
    

def _get_breadcrumbs(query, dir_name, page):
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
    querystring= ''
    for k,v in items:
        if k != var_1 and k != var_2 and k != var_3:
            querystring = querystring + "&" + k + "=" + v
    return querystring
    

def _get_query(request_var):
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
    filesize_str = ''
    if filesize_long < 1000:
        filesize_str = str(filesize_long) + "&nbsp;B"
    elif filesize_long >= 1000 and filesize_long < 1000000:
        filesize_str = str(filesize_long/1000) + "&nbsp;kB"
    elif filesize_long >= 1000000:
        filesize_str = str(filesize_long/1000000) + "&nbsp;MB"
    return filesize_str
    

def _make_filedict(file_list):
    ''' Make a dict out of the file_list (This is for better readability in the templates only)
    '''
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
    settings_var['IMAGE_GENERATOR'] = IMAGE_GENERATOR
    settings_var['USE_SNIPSHOT'] = USE_SNIPSHOT
    settings_var['USE_PICNIK'] = USE_PICNIK
    settings_var['PICNIK_KEY'] = PICNIK_KEY
    settings_var['CALLBACK_URL'] = "http://" + http_post + URL_ADMIN + path
    return settings_var
    

def index(request, dir_name=None):
    ''' Show list of files on a server-directory
    '''
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    results_var = {'results_total': 0, 'results_current': 0, 'delete_total': 0, 'change_total': 0 }
    counter = {}
    for k,v in EXTENSIONS.iteritems():
        counter[k] = 0
    dir_list = os.listdir(os.path.join(PATH_SERVER, path))
    
    file_list = []
    for file in dir_list:
        
        # VARIABLES
        filesize_long = '' # filesize
        filesize_str = '' # filesize in B, kB, MB
        date = '' # YYYY-MM-dd
        path_thumb = '' # path to thumbnail
        link = '' # link to file (using URL_WWW), link to folder (using URL_ADMIN)
        select_link = '' # link to file (using URL_WWW)
        file_extension = '' # see EXTENSIONS in fb_settings.py
        file_type = '' # Folder, Image, Video, Document, Sound, Code
        image_dimensions = '' # (width, height)
        thumb_dimensions = '' # (width, height)
        flag_makethumb = False # Boolean
        flag_deletedir = False # Boolean
        snipshot_output_options = '' # JSON (Filename)
        
        # DON'T DISPLAY FILES STARTING WITH %THUMB_PREFIX%
        if re.compile(THUMB_PREFIX, re.M).search(file) or \
        file.startswith('.'): # ... or with a '.' \
            continue
        else:
            results_var['results_total'] = results_var['results_total'] + 1
        
        # SIZE
        filesize_long = os.path.getsize(os.path.join(PATH_SERVER, path, file))
        filesize_str = _get_filesize(filesize_long)
        
        # DATE / TIME
        date_time = os.path.getmtime(os.path.join(PATH_SERVER, path, file))
        date = strftime("%Y-%m-%d", gmtime(date_time))
        
        # EXTENSION / FLAG_EMPTYDIR / DELETE_TOTAL
        if os.path.isfile(os.path.join(PATH_SERVER, path, file)): # file
            file_extension = os.path.splitext(file)[1].lower()
            link = "%s%s%s" % (URL_WWW, path, file)
            select_link = link
        elif os.path.isdir(os.path.join(PATH_SERVER, path, file)): # folder
            link = "%s%s%s" % (URL_ADMIN, path, file)
            select_link = "%s%s%s/" % (URL_WWW, path, file)
            if not os.listdir(os.path.join(PATH_SERVER, path, file)):
                flag_deletedir = True
        
        # FILETYPE / COUNTER
        for k,v in EXTENSIONS.iteritems():
            for extension in v:
                if file_extension == extension.lower():
                    file_type = k
                    counter[k] = counter[k] + 1
        
        # DIMENSIONS / MAKETHUMB / SELECT
        if file_type == 'Image':
            try:
                im = Image.open(os.path.join(PATH_SERVER, path, file))
                image_dimensions = im.size
                path_thumb = "%s%s%s%s" % (URL_WWW, path, THUMB_PREFIX, file)
                try:
                    thmb = Image.open(os.path.join(PATH_SERVER, path, THUMB_PREFIX + file))
                    thumb_dimensions = thmb.size
                except:
                    path_thumb = settings.ADMIN_MEDIA_PREFIX + 'filebrowser/img/filebrowser_Thumb.gif'
                    flag_makethumb = True
            except:
                # if image is corrupt, change filetype to not defined
                file_type = ''
                path_thumb = settings.ADMIN_MEDIA_PREFIX + 'filebrowser/img/filebrowser_' + file_type + '.gif'
        else:
            path_thumb = settings.ADMIN_MEDIA_PREFIX + 'filebrowser/img/filebrowser_' + file_type + '.gif'
        
        # FILTER / SEARCH
        flag_extend = False
        if query['filter_type'] != '' and query['filter_date'] != '' and file_type == query['filter_type'] and _get_filterdate(query['filter_date'], date_time):
            flag_extend = True
        elif query['filter_type'] != '' and query['filter_date'] == '' and file_type == query['filter_type']:
            flag_extend = True
        elif query['filter_type'] == '' and query['filter_date'] != '' and _get_filterdate(query['filter_date'], date_time):
            flag_extend = True
        elif query['filter_type'] == '' and query['filter_date'] == '':
            flag_extend = True
        if query['q'] and not re.compile(query['q'].lower(), re.M).search(file.lower()):
            flag_extend = False
        
        # APPEND FILE_LIST
        if flag_extend == True:
            file_list.append([file, filesize_long, filesize_str, date, path_thumb, link, select_link, file_extension,file_type, image_dimensions, thumb_dimensions,file.lower(), flag_makethumb, flag_deletedir])
    
    # SORT LIST
    file_list.sort(lambda x, y: cmp(x[int(query['o'])], y[int(query['o'])]))
    if query['ot'] == "desc":
       file_list.reverse()
    
    # MAKE DICTIONARY (for better readability in the templates)
    file_dict = _make_filedict(file_list)
    
    # RESULTS
    results_var['results_current'] = len(file_list)
    for file in file_dict:
        if file['file_type'] == 'Image':
            results_var['change_total'] = results_var['change_total'] + 1
        if file['file_type'] != 'Folder':
            results_var['delete_total'] = results_var['delete_total'] + 1
        elif file['file_type'] == 'Folder' and file['flag_deletedir'] == True:
            results_var['delete_total'] = results_var['delete_total'] + 1
    
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'file_dict': file_dict,
        'results_var': results_var,
        'query': query,
        'counter': counter,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, ''),
        'title': _('FileBrowser'),
    }, context_instance=Context(request))
index = staff_member_required(never_cache(index))


def mkdir(request, dir_name=None):
    ''' Make directory
    '''
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    alnum_name_re = re.compile(r'^[a-zA-Z0-9_-]+$')
    error = {}
    if request.POST:
        if request.POST.get('name'):
            if not alnum_name_re.search(request.POST.get('name')):
                error['headline'] = _('Please correct the errors below.')
                error['error_msg'] = _('Only letters, numbers, underscores and hyphens are allowed.')
            else:
                server_path = os.path.join(PATH_SERVER, path, request.POST.get('name').lower())
                try:
                    os.mkdir(server_path)
                    os.chmod(server_path, 0775)
                    msg = _('The directory %s was successfully created.') % (request.POST.get('name').lower())
                    request.user.message_set.create(message=msg)
                    # on redirect, sort by date desc to see the new directory on top of the list
                    return HttpResponseRedirect(URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop'])
                except OSError, (errno, strerror):
                    if errno == 17:
                        error['headline'] = _('The directory %s already exists.') % (request.POST.get('name').lower())
                    elif errno == 13:
                        error['headline'] = _('Permission denied.')
                    else:
                        pass
        else:
            error['headline'] = _('Please correct the errors below.')
            error['error_msg'] = _('This field is required.')
    
    return render_to_response('filebrowser/makedir.html', {
        'dir': dir_name,
        'error': error,
        'query': query,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, 'Make Directory'),
        'title': _('Make directory'),
    }, context_instance=Context(request))
mkdir = staff_member_required(never_cache(mkdir))


def upload(request, dir_name=None):
    ''' Multiple Upload
    '''
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    alnum_name_re = re.compile(r'^[a-zA-Z0-9._/-]+$')
    
    # PIL's Fehler "Suspension not allowed here" work around:
    # s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
    import ImageFile
    ImageFile.MAXBLOCK = 1000000 # default is 64k
    
    error_list = []
    success_msg = ""
    if request.GET.get('action') == 'upload':
        if request.FILES:
            checkbox_counter = 1
            for file in request.FILES.getlist('file'):
                filename = file['filename']
                error_msg = ""
                # CHECK IF FILE ALREADY EXISTS
                file_exists = False
                dir_list = os.listdir(os.path.join(PATH_SERVER, path))
                for entry in dir_list:
                    if filename == entry:
                        file_exists = True
                
                if not file_exists:
                    # CHECK FILENAME
                    if alnum_name_re.search(filename):
                        # CHECK EXTENSION / FILE_TYPE
                        file_extension = os.path.splitext(filename)[1].lower()
                        if file_extension == "":
                            file_extension='unknown'
                        file_type = ''
                        for k,v in EXTENSIONS.iteritems():
                            for extension in v:
                                if file_extension == extension.lower():
                                    file_type = k
                        
                        # UPLOAD
                        if file_type != '':
                            file = file['content']
                            length = len(file)
                            
                            # CHECK FILESIZE
                            if length < MAX_UPLOAD_SIZE:
                                
                                # UPLOAD FILE
                                file_path = os.path.join(PATH_SERVER, path, filename)
                                f = open(file_path, 'wb')
                                f.write(file)
                                os.chmod(file_path, 0664)
                                f.close()
                                
                                # MAKE THUMBNAIL
                                if file_type == 'Image':
                                    thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + filename)
                                    try:
                                        im = Image.open(file_path)
                                        im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                                        im.save(thumb_path)
                                    except IOError:
                                        error_msg = "<b>%s:</b> %s" % (filename, _('Thumbnail creation failed.'))
                                        error_list.append([error_msg])
                                        
                                # MAKE ADDITIONAL IMAGE VERSIONS
                                checkbox = "checkbox_" + str(checkbox_counter)
                                use_image_generator = request.POST.get(checkbox)
                                im = Image.open(file_path)
                                if use_image_generator and IMAGE_GENERATOR != "":
                                    for prefix in IMAGE_GENERATOR:
                                        image_path = os.path.join(PATH_SERVER, path, prefix[0] + filename)
                                        try:
                                            # DIMENSIONS
                                            dimensions = im.size
                                            current_width = dimensions[0]
                                            current_height = dimensions[1]
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
                                                # MAKE THUMBNAILS FOR EACH IMAGE VERSION
                                                thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + prefix[0] + filename)
                                                try:
                                                    new_image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                                                    new_image.save(thumb_path)
                                                except IOError:
                                                    error_msg = "<b>%s:</b> %s" % (filename, _('Thumbnail creation failed.'))
                                                    error_list.append([error_msg])
                                        except IOError:
                                            error_msg = "<b>%s:</b> %s" % (filename, _('Image creation failed.'))
                                            error_list.append([error_msg])
                                            
                                # GENERATE CROPPED/RECTANGULAR IMAGE
                                if use_image_generator and IMAGE_CROP_GENERATOR != "":
                                    for prefix in IMAGE_CROP_GENERATOR:
                                        image_path = os.path.join(PATH_SERVER, path, prefix[0] + filename)
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
                                            # MAKE THUMBNAILS FOR EACH IMAGE VERSION
                                            thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + prefix[0] + filename)
                                            try:
                                                cropped_image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                                                cropped_image.save(thumb_path)
                                            except IOError:
                                                error_msg = "<b>%s:</b> %s" % (filename, _('Thumbnail creation failed.'))
                                                error_list.append([error_msg])
                                        except IOError:
                                            error_msg = "<b>%s:</b> %s" % (filename, _('Image creation failed.'))
                                            error_list.append([error_msg])
                                    
                                    
                                
                            else:
                                error_msg = "<b>%s:</b> %s" % (filename, _('Filesize exceeds allowed Upload Size.'))
                                error_list.append([error_msg])
                        else:
                            error_msg = "<b>%s:</b> %s" % (filename, _('File extension is not allowed.'))
                            error_list.append([error_msg])
                    else:
                        error_msg = "<b>%s:</b> %s" % (filename, _('Filename is not allowed.'))
                        error_list.append([error_msg])
                else:
                    error_msg = "<b>%s:</b> %s" % (filename, _('File already exists.'))
                    error_list.append([error_msg])
                if error_msg == "":
                    success_msg = success_msg + filename + ","
                
            success_msg = success_msg.rstrip(",")
            if not error_list:
                msg = "%s%s" % (_('Successfully uploaded '), success_msg)
                request.user.message_set.create(message=msg)
                # on redirect, sort by date desc to see the uploaded files on top of the list
                redirect_url = URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop']
                return HttpResponseRedirect(redirect_url)
            elif success_msg != "":
                msg = "%s%s" % (_('Successfully uploaded '), success_msg)
                request.user.message_set.create(message=msg)
        else:
            error_msg = _('At least one file must be chosen.')
            error_list.append([error_msg])
        checkbox_counter = checkbox_counter + 1
            
    
    return render_to_response('filebrowser/upload.html', {
        'dir': dir_name,
        'error_list': error_list,
        'query': _get_query(request.GET),
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, 'Multiple Upload'),
        'title': _('Select files to upload'),
    }, context_instance=Context(request))
upload = staff_member_required(never_cache(upload))


def makethumb(request, dir_name=None, file_name=None):
    ''' Make Thumbnail(s) for existing Image or Directory
        This is useful if someone uploads images via FTP, not using the
        upload functionality of the FileBrowser.
    '''
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    if file_name:
        file_path = os.path.join(PATH_SERVER, path, file_name)
        try:
            im = Image.open(file_path)
            im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
            try:
                im.save(os.path.join(PATH_SERVER, path, THUMB_PREFIX + file_name))
                msg = _('The Thumbnail was succesfully created.')
            except IOError:
                msg = _('Thumbnail creation failed.')
        except IOError:
            msg = _('File does not exist.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(URL_ADMIN + path + query['query_str_total'])
        
    else:
        dir_path = os.path.join(PATH_SERVER, path)
        dir_list = os.listdir(dir_path)
        msg = ""
        for file in dir_list:
            if re.compile(THUMB_PREFIX, re.M).search(file):
                continue
            else:
                if os.path.isfile(os.path.join(PATH_SERVER, path, file)): # file
                    file_extension = os.path.splitext(file)[1].lower()
                else:
                    continue
                for k,v in EXTENSIONS.iteritems():
                    for extension in v:
                        if file_extension == extension.lower():
                            file_type = k
                            
                if file_type == 'Image':
                    if os.path.isfile(os.path.join(PATH_SERVER, path, THUMB_PREFIX + file)):
                        continue
                    else:
                        file_path = os.path.join(PATH_SERVER, path, file)
                        thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + file)
                        try:
                            im = Image.open(file_path)
                            im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                            im.save(thumb_path)
                            msg = _('The Thumbnails were succesfully created.')
                        except IOError:
                            pass
        if msg:
            request.user.message_set.create(message=msg)
        return HttpResponseRedirect(URL_ADMIN + path + query['query_str_total'])
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'query': query,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, '')
    }, context_instance=Context(request))
makethumb = staff_member_required(never_cache(makethumb))


def delete(request, dir_name=None):
    ''' Delete existing File/Directory.
        If file is an Image, also delete thumbnail.
        When trying to delete a directory, the directory has to be empty.
    '''
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    msg = ""
    
    if request.GET:
        if request.GET.get('type') != "Folder":
            server_path = os.path.join(PATH_SERVER, path, request.GET.get('filename'))
            try:
                os.unlink(server_path)
                path_thumb = os.path.join(PATH_SERVER, path, THUMB_PREFIX + request.GET.get('filename'))
                try:
                    os.unlink(path_thumb)
                except OSError: # thumbnail does not exist
                    pass
                msg = _('The file %s was successfully deleted.') % (request.GET.get('filename').lower())
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(URL_ADMIN + path + query['query_nodelete'])
            except OSError:
                msg = OSError
        else:
            server_path = os.path.join(PATH_SERVER, path, request.GET.get('filename'))
            try:
                os.rmdir(server_path)
                msg = _('The directory %s was successfully deleted.') % (request.GET.get('filename').lower())
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(URL_ADMIN + path + query['query_nodelete'])
            except OSError:
                msg = OSError
    
    if msg:
        request.user.message_set.create(message=msg)
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'file': request.GET.get('filename', ''),
        'query': query,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, '')
    }, context_instance=Context(request))
delete = staff_member_required(never_cache(delete))


def rename(request, dir_name=None, file_name=None):
    ''' Rename existing File/Directory.
    '''
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    alnum_name_re = re.compile(r'^[a-zA-Z0-9_-]+$')
    error = {}
    
    if os.path.isfile(os.path.join(PATH_SERVER, path, file_name)): # file
        file_extension = os.path.splitext(file_name)[1].lower()
        for k,v in EXTENSIONS.iteritems():
            for extension in v:
                if file_extension == extension.lower():
                    file_type = k
    else:
        file_extension = ""
        file_type = ""
    
    if request.POST:
        if request.POST.get('name'):
            if not alnum_name_re.search(request.POST.get('name')):
                error['headline'] = _('Please correct the errors below.')
                error['error_msg'] = _('Only letters, numbers, underscores and hyphens are allowed.')
            else:
                old_path = os.path.join(PATH_SERVER, path, file_name)
                new_path = os.path.join(PATH_SERVER, path, request.POST.get('name').lower() + file_extension)
                if not os.path.isdir(new_path) and not os.path.isfile(new_path):
                    try:
                        os.rename(old_path, new_path)
                        if file_type == 'Image':
                            old_thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + file_name)
                            new_thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + request.POST.get('name').lower() + file_extension)
                            try:
                                os.rename(old_thumb_path, new_thumb_path)
                            except:
                                pass
                        msg = _('Renaming was successful.')
                        request.user.message_set.create(message=msg)
                        # on redirect, sort by date desc to see the new directory on top of the list
                        return HttpResponseRedirect(URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop'])
                    except OSError, (errno, strerror):
                        pass
                else:
                    error['headline'] = _('Please correct the errors below.')
                    error['error_msg'] = _('The new file/directory already exists.')
        else:
            error['headline'] = _('Please correct the errors below.')
            error['error_msg'] = _('This field is required.')
    
    return render_to_response('filebrowser/rename.html', {
        'dir': dir_name,
        'error': error,
        'query': query,
        'file_name': file_name,
        'file_extension': file_extension,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, ''),
        'title': _('Rename "%s"') % file_name,
    }, context_instance=Context(request))
rename = staff_member_required(never_cache(rename))


def snipshot_callback(request, dir_name=None):
    ''' Get file from snipshot and save it over existing file (also change thumbnail)
    '''
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    alnum_name_re = re.compile(r'^[a-zA-Z0-9_-]+$')
    error = {}
    
    if request.FILES:
        for file in request.FILES.getlist('file'):
            filename = file['filename']
            # DELETE OLD FILE
            file_path = os.path.join(PATH_SERVER, path, filename)
            try:
                os.unlink(file_path)
                path_thumb = os.path.join(PATH_SERVER, path, THUMB_PREFIX + filename)
                try:
                    os.unlink(path_thumb)
                except OSError: # thumbnail does not exist
                    pass
            except OSError:
                msg = OSError
            
            # UPLOAD NEW FILE
            file_path = os.path.join(PATH_SERVER, path, filename)
            f = open(file_path, 'wb')
            f.write(file['content'])
            os.chmod(file_path, 0664)
            f.close()
            
            # MAKE THUMBNAIL
            thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + filename)
            try:
                im = Image.open(file_path)
                im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                im.save(thumb_path)
            except IOError:
                pass
            
            # on redirect, sort by date desc to see the new file
            redirect_url = URL_ADMIN + path + "?&ot=desc&o=3&"
            return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponseRedirect(URL_ADMIN + path)
        
#snipshot_callback = staff_member_required(never_cache(snipshot_callback))


def picnik_callback(request, dir_name=None):
    ''' Get file from snipshot and save it over existing file (also change thumbnail)
    '''
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    alnum_name_re = re.compile(r'^[a-zA-Z0-9_-]+$')
    error = {}
    old_filename = ""
    
    if request.POST:
        old_filename = request.POST.get('_imageid')
    if request.FILES:
        for file in request.FILES.getlist('file'):
            filename = file['filename'].lstrip('images/')
            if old_filename:
                filename = old_filename
                # DELETE OLD FILE
                file_path = os.path.join(PATH_SERVER, path, filename)
                try:
                    os.unlink(file_path)
                    path_thumb = os.path.join(PATH_SERVER, path, THUMB_PREFIX + filename)
                    try:
                        os.unlink(path_thumb)
                    except OSError: # thumbnail does not exist
                        pass
                except OSError:
                    msg = OSError
            
            # UPLOAD NEW FILE
            file_path = os.path.join(PATH_SERVER, path, filename)
            f = open(file_path, 'wb')
            f.write(file['content'])
            os.chmod(file_path, 0664)
            f.close()
            
            # MAKE THUMBNAIL
            thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + filename)
            try:
                im = Image.open(file_path)
                im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                im.save(thumb_path)
            except IOError:
                pass
            
            # on redirect, sort by date desc to see the new file
            redirect_url = SNIPSHOT_CALLBACK_URL + path + "?&ot=desc&o=3&"
            return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponseRedirect(URL_ADMIN + path)
        
#picnik_callback = staff_member_required(never_cache(picnik_callback))
