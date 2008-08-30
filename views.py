from django.shortcuts import render_to_response
from django.template import RequestContext as Context
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from time import gmtime, strftime, localtime, mktime, time
import os, string, ftplib, re, Image, decimal
from django import forms

# get settings
from filebrowser.fb_settings import *
# get functions
from filebrowser.functions import _get_path, _get_subdir_list, _get_dir_list, _get_breadcrumbs, _get_sub_query, _get_query, _get_filterdate, _get_filesize, _make_filedict, _get_settings_var, _handle_file_upload, _get_file_type, _make_image_thumbnail, _image_generator, _image_crop_generator
# get forms
from filebrowser.forms import MakeDirForm, RenameForm, UploadForm, BaseUploadFormSet


def index(request, dir_name=None):
    """
    Show list of files on a server-directory.
    """
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    # INITIAL VARIABLES
    results_var = {'results_total': 0, 'results_current': 0, 'delete_total': 0, 'change_total': 0 }
    counter = {}
    for k,v in EXTENSIONS.iteritems():
        counter[k] = 0
    
    dir_list = os.listdir(os.path.join(PATH_SERVER, path))
    file_list = []
    for file in dir_list:
        
        # VARIABLES
        var_filesize_long = '' # filesize
        var_filesize_str = '' # filesize in B, kB, MB
        var_date = '' # YYYY-MM-dd
        var_path_thumb = '' # path to thumbnail
        var_link = '' # link to file (using URL_WWW), link to folder (using URL_ADMIN)
        var_select_link = '' # link to file (using URL_WWW)
        var_file_extension = '' # see EXTENSIONS in fb_settings.py
        var_file_type = '' # Folder, Image, Video, Document, Sound, Code, ...
        var_image_dimensions = '' # (width, height)
        var_thumb_dimensions = '' # (width, height)
        var_flag_makethumb = False # Boolean
        var_flag_deletedir = False # Boolean
        
        # DON'T DISPLAY FILES STARTING WITH %THUMB_PREFIX% OR "."
        if re.compile(THUMB_PREFIX, re.M).search(file) or \
        file.startswith('.'): # ... or with a '.' \
            continue
        else:
            results_var['results_total'] += 1
        
        # SIZE
        var_filesize_long = os.path.getsize(os.path.join(PATH_SERVER, path, file))
        var_filesize_str = _get_filesize(var_filesize_long)
        
        # DATE / TIME
        date_time = os.path.getmtime(os.path.join(PATH_SERVER, path, file))
        var_date = strftime("%Y-%m-%d", gmtime(date_time))
        
        # EXTENSION / FLAG_EMPTYDIR / DELETE_TOTAL
        if os.path.isfile(os.path.join(PATH_SERVER, path, file)): # file
            var_file_extension = os.path.splitext(file)[1].lower()
            var_select_link = var_link = "%s%s%s" % (URL_WWW, path, file)
        elif os.path.isdir(os.path.join(PATH_SERVER, path, file)): # folder
            var_link = "%s%s%s" % (URL_ADMIN, path, file)
            var_select_link = "%s%s%s/" % (URL_WWW, path, file)
            if not os.listdir(os.path.join(PATH_SERVER, path, file)):
                var_flag_deletedir = True # only empty directories are allowed to be deleted
        
        # FILETYPE / COUNTER
        var_file_type = _get_file_type(file)
        if var_file_type:
            counter[var_file_type] += 1
        
        # DIMENSIONS / MAKETHUMB / SELECT
        if var_file_type == 'Image':
            try:
                im = Image.open(os.path.join(PATH_SERVER, path, file))
                var_image_dimensions = im.size
                var_path_thumb = "%s%s%s%s" % (URL_WWW, path, THUMB_PREFIX, file)
                try:
                    thumb = Image.open(os.path.join(PATH_SERVER, path, THUMB_PREFIX + file))
                    var_thumb_dimensions = thumb.size
                except:
                    # if thumbnail does not exist, show makethumb-Icon instead.
                    var_path_thumb = settings.ADMIN_MEDIA_PREFIX + 'filebrowser/img/filebrowser_Thumb.gif'
                    var_flag_makethumb = True
            except:
                # if image is corrupt, change filetype to not defined
                var_file_type = ''
        
        # FILTER / SEARCH
        flag_extend = False
        if query['filter_type'] != '' and query['filter_date'] != '' and file_type == query['filter_type'] and _get_filterdate(query['filter_date'], date_time):
            flag_extend = True
        elif query['filter_type'] != '' and query['filter_date'] == '' and var_file_type == query['filter_type']:
            flag_extend = True
        elif query['filter_type'] == '' and query['filter_date'] != '' and _get_filterdate(query['filter_date'], date_time):
            flag_extend = True
        elif query['filter_type'] == '' and query['filter_date'] == '':
            flag_extend = True
        if query['q'] and not re.compile(query['q'].lower(), re.M).search(file.lower()):
            flag_extend = False
        
        # APPEND FILE_LIST
        if flag_extend == True:
            file_list.append([file, var_filesize_long, var_filesize_str, var_date, var_path_thumb, var_link, var_select_link, var_file_extension, var_file_type, var_image_dimensions, var_thumb_dimensions, file.lower(), var_flag_makethumb, var_flag_deletedir])
    
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
            results_var['change_total'] += 1
        if file['file_type'] != 'Folder':
            results_var['delete_total'] += 1
        elif file['file_type'] == 'Folder' and file['flag_deletedir'] == True:
            results_var['delete_total'] += 1
    
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
    """
    Make directory
    """
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    if request.method == 'POST':
        form = MakeDirForm(PATH_SERVER, path, request.POST)
        if form.is_valid():
            server_path = os.path.join(PATH_SERVER, path, form.cleaned_data['dir_name'].lower())
            try:
                os.mkdir(server_path)
                os.chmod(server_path, 0775)
                
                # MESSAGE & REDIRECT
                msg = _('The directory %s was successfully created.') % (form.cleaned_data['dir_name'].lower())
                request.user.message_set.create(message=msg)
                # on redirect, sort by date desc to see the new directory on top of the list
                return HttpResponseRedirect(URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop'])
            except OSError, (errno, strerror):
                if errno == 13:
                    form.errors['dir_name'] = forms.util.ErrorList([_('Permission denied.')])
                else:
                    form.errors['dir_name'] = forms.util.ErrorList([_('Error creating directory.')])
    else:
        form = MakeDirForm(PATH_SERVER, path)
    
    return render_to_response('filebrowser/makedir.html', {
        'form': form,
        'query': query,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, 'Make Directory'),
        'title': _('Make directory'),
    }, context_instance=Context(request))
mkdir = staff_member_required(never_cache(mkdir))


def upload(request, dir_name=None):
    """
    Multipe Upload.
    """
    
    from django.forms.formsets import formset_factory
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    # PIL's Error "Suspension not allowed here" work around:
    # s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
    import ImageFile
    ImageFile.MAXBLOCK = 1000000 # default is 64k
    
    UploadFormSet = formset_factory(UploadForm, formset=BaseUploadFormSet, extra=5)
    if request.method == 'POST':
        formset = UploadFormSet(data=request.POST, files=request.FILES, path_server=PATH_SERVER, path=path)
        if formset.is_valid():
            for cleaned_data in formset.cleaned_data:
                if cleaned_data:
                    # UPLOAD FILE
                    _handle_file_upload(PATH_SERVER, path, cleaned_data['file'])
                    if _get_file_type(cleaned_data['file'].name) == "Image":
                        # MAKE THUMBNAIL
                        _make_image_thumbnail(PATH_SERVER, path, cleaned_data['file'].name)
                        # IMAGE GENERATOR
                        if cleaned_data['use_image_generator'] and (IMAGE_GENERATOR_LANDSCAPE != "" or IMAGE_GENERATOR_PORTRAIT != ""):
                            _image_generator(PATH_SERVER, path, cleaned_data['file'].name)
                        # GENERATE CROPPED/RECTANGULAR IMAGE
                        if cleaned_data['use_image_generator'] and IMAGE_CROP_GENERATOR != "":
                            _image_crop_generator(PATH_SERVER, path, cleaned_data['file'].name)
            # MESSAGE & REDIRECT
            msg = _('Upload successful.')
            request.user.message_set.create(message=msg)
            # on redirect, sort by date desc to see the uploaded files on top of the list
            redirect_url = URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop']
            return HttpResponseRedirect(redirect_url)
    else:
        formset = UploadFormSet(path_server=PATH_SERVER, path=path)
    
    return render_to_response('filebrowser/upload.html', {
        'formset': formset,
        'dir': dir_name,
        'query': _get_query(request.GET),
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, 'Multiple Upload'),
        'title': _('Select files to upload'),
    }, context_instance=Context(request))
upload = staff_member_required(never_cache(upload))


def makethumb(request, dir_name=None, file_name=None):
    """
    Make Thumbnail(s) for existing Image or Directory
        This is useful if someone uploads images via FTP, not using the
        upload functionality of the FileBrowser.
    """
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    if file_name:
        # MAKE THUMB FOR SINGLE IMAGE
        file_path = os.path.join(PATH_SERVER, path, file_name)
        if os.path.isfile(file_path):
            _make_image_thumbnail(PATH_SERVER, path, file_name)
    else:
        # MAKE THUMBS FOR WHOLE DIRECTORY
        dir_path = os.path.join(PATH_SERVER, path)
        dir_list = os.listdir(dir_path)
        for file in dir_list:
            if os.path.isfile(os.path.join(PATH_SERVER, path, file)) and not os.path.isfile(os.path.join(PATH_SERVER, path, THUMB_PREFIX + file)) and not re.compile(THUMB_PREFIX, re.M).search(file) and _get_file_type(file) == "Image":
                _make_image_thumbnail(PATH_SERVER, path, file)
    
    # MESSAGE & REDIRECT
    msg = _('Thumbnail creation successful.')
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
    """
    Delete existing File/Directory.
        If file is an Image, also delete thumbnail.
        When trying to delete a directory, the directory has to be empty.
    """
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    msg = ""
    
    if request.GET:
        if request.GET.get('type') != "Folder":
            server_path = os.path.join(PATH_SERVER, path, request.GET.get('filename'))
            try:
                
                # DELETE FILE
                os.unlink(server_path)
                # TRY DELETING THUMBNAIL
                path_thumb = os.path.join(PATH_SERVER, path, THUMB_PREFIX + request.GET.get('filename'))
                try:
                    os.unlink(path_thumb)
                except OSError:
                    pass
                # TRY DELETING IMAGE_VERSIONS
                versions_path = os.path.join(PATH_SERVER, path, request.GET.get('filename').replace(".", "_").lower() + IMAGE_GENERATOR_DIRECTORY)
                try:
                    dir_list = os.listdir(versions_path)
                    for file in dir_list:
                        file_path = os.path.join(versions_path, file)
                        os.unlink(file_path)
                    os.rmdir(versions_path)
                except OSError:
                    pass
                
                # MESSAGE & REDIRECT
                msg = _('The file %s was successfully deleted.') % (request.GET.get('filename').lower())
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(URL_ADMIN + path + query['query_nodelete'])
            except OSError:
                # todo: define error message
                msg = OSError
        else:
            server_path = os.path.join(PATH_SERVER, path, request.GET.get('filename'))
            try:
                os.rmdir(server_path)
                
                # MESSAGE & REDIRECT
                msg = _('The directory %s was successfully deleted.') % (request.GET.get('filename').lower())
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(URL_ADMIN + path + query['query_nodelete'])
            except OSError:
                # todo: define error message
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
    """
    Rename existing File/Directory.
    """
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    if os.path.isfile(os.path.join(PATH_SERVER, path, file_name)): # file
        file_type = _get_file_type(file_name)
        file_extension = os.path.splitext(file_name)[1].lower()
    else:
        file_extension = ""
        file_type = ""
    
    if request.method == 'POST':
        form = RenameForm(PATH_SERVER, path, file_extension, request.POST)
        if form.is_valid():
            old_path = os.path.join(PATH_SERVER, path, file_name)
            new_path = os.path.join(PATH_SERVER, path, request.POST.get('name').lower() + file_extension)
            try:
                os.rename(old_path, new_path)
                
                # RENAME IMAGE_THUMBNAILS
                if file_type == 'Image':
                    old_thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + file_name)
                    new_thumb_path = os.path.join(PATH_SERVER, path, THUMB_PREFIX + request.POST.get('name').lower() + file_extension)
                    try:
                        os.rename(old_thumb_path, new_thumb_path)
                    except OSError, (errno, strerror):
                        form.errors['name'] = forms.util.ErrorList([_('Error renaming Thumbnail.')])
                    
                    # RENAME IMAGE VERSIONS? TOO MUCH MAGIC?
                
                # MESSAGE & REDIRECT
                if not form.errors:
                    msg = _('Renaming was successful.')
                    request.user.message_set.create(message=msg)
                    # on redirect, sort by date desc to see the new stuff on top of the list
                    return HttpResponseRedirect(URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop'])
            except OSError, (errno, strerror):
                form.errors['name'] = forms.util.ErrorList([_('Error.')])
    else:
        form = RenameForm(PATH_SERVER, path, file_extension)
    
    return render_to_response('filebrowser/rename.html', {
        'form': form,
        'query': query,
        'file_extension': file_extension,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, ''),
        'title': _('Rename "%s"') % file_name,
    }, context_instance=Context(request))
rename = staff_member_required(never_cache(rename))


def generateimages(request, dir_name=None, file_name=None):
    """
    Generate Image Versions for existing singe Image or a whole Directory.
        This is useful if someone uploads images via FTP, not using the
        upload functionality of the FileBrowser.
    """
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    if file_name:
        # GENERATE IMAGES
        if IMAGE_GENERATOR_LANDSCAPE != "" or IMAGE_GENERATOR_PORTRAIT != "":
            _image_generator(PATH_SERVER, path, file_name)
        # GENERATE CROPPED/RECTANGULAR IMAGE
        if IMAGE_CROP_GENERATOR != "":
            _image_crop_generator(PATH_SERVER, path, file_name)
    else:
        # GENERATE IMAGES FOR WHOLE DIRECTORY
        dir_path = os.path.join(PATH_SERVER, path)
        dir_list = os.listdir(dir_path)
        for file in dir_list:
            if os.path.isfile(os.path.join(PATH_SERVER, path, file)) and not re.compile(THUMB_PREFIX, re.M).search(file) and _get_file_type(file) == "Image":
                # GENERATE IMAGES
                if IMAGE_GENERATOR_LANDSCAPE != "" or IMAGE_GENERATOR_PORTRAIT != "":
                    _image_generator(PATH_SERVER, path, file)
                # GENERATE CROPPED/RECTANGULAR IMAGE
                if IMAGE_CROP_GENERATOR != "":
                    _image_crop_generator(PATH_SERVER, path, file)
    
    # MESSAGE & REDIRECT
    msg = _('Successfully generated Images.')
    request.user.message_set.create(message=msg)
    return HttpResponseRedirect(URL_ADMIN + path + query['query_str_total'])
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'query': query,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, '')
    }, context_instance=Context(request))
makethumb = staff_member_required(never_cache(makethumb))


