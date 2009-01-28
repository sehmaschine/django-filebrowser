# coding: utf-8

import time
import os, string, ftplib, re, Image, decimal
from time import gmtime, strftime, localtime, mktime
from datetime import datetime, timedelta

from django.shortcuts import render_to_response
from django.template import loader, RequestContext as Context
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.simple import direct_to_template
from django.views.decorators.cache import never_cache
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import forms

# get settings
from filebrowser.fb_settings import *
from filebrowser.models import File, ImageModification
from filebrowser.templatetags.filebrowser import modified_path
# get functions
from filebrowser.functions import _get_path, _get_subdir_list, _get_dir_list, _get_breadcrumbs, _get_sub_query, _get_query, _get_filterdate, _get_filesize, _get_settings_var, _handle_file_upload, _get_file_type, _make_image_thumbnail, _image_generator, _image_crop_generator, _is_image_version, locate
# get forms
from filebrowser.forms import MakeDirForm, RenameForm, UploadSettingsForm, UploadForm, ChangeForm, BaseUploadFormSet

### don't display files starting with %THUMB_PREFIX%
### don't display system files
### don't display _cache folders
HIDDEN_FILE_PATTERN = getattr(
    settings,
    "HIDDEN_FILE_PATTERN",
    re.compile(r'^(%s|\.|_cache)' % re.escape(THUMB_PREFIX), re.M),
    )

def index(request, dir_name=""):
    """
    Show list of files on a server-directory.
    """
    if not request.user.has_perm("filebrowser.browse_file"):
        t = loader.get_template("403.html")
        return HttpResponseForbidden(t.render(RequestContext(request)))
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    # INITIAL VARIABLES
    results_var = {'results_total': 0, 'results_current': 0, 'delete_total': 0, 'change_total': 0, 'imagegenerator_total': 0 }
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
        var_image_dimensions = '' # Image Dimensions (width, height)
        var_thumb_dimensions = '' # Thumbnail Dimensions (width, height)
        var_flag_makethumb = False # True, if Image has no Thumbnail.
        var_flag_deletedir = False # True, if Directory is empty.
        var_image_version = False # True, if Image is generated with ImageGenerator.
        
        if HIDDEN_FILE_PATTERN.search(file):
            continue
        else:
            results_var['results_total'] += 1
        
        # SIZE
        var_filesize_long = os.path.getsize(os.path.join(PATH_SERVER, path, file))
        
        # DATE / TIME
        date_time = os.path.getmtime(os.path.join(PATH_SERVER, path, file))
        var_date = strftime("%Y-%m-%d", gmtime(date_time))
        
        # EXTENSION / FLAG_EMPTYDIR / DELETE_TOTAL
        if os.path.isfile(os.path.join(PATH_SERVER, path, file)): # file
            var_file_extension = os.path.splitext(file)[1].lower()
            var_select_link = var_link = "%s%s" % (path, file)
        elif os.path.isdir(os.path.join(PATH_SERVER, path, file)): # folder
            var_link = "%s%s%s" % (URL_ADMIN, path, file)
            var_select_link = "%s%s/" % (path, file)
            sub_dir_path = os.path.join(PATH_SERVER, path, file)
            sub_dir_list = os.listdir(sub_dir_path)
            var_flag_deletedir = (
                not len(sub_dir_list)
                or (len(sub_dir_list)==1 and "_cache" in sub_dir_list)
                ) # only empty directories are allowed to be deleted
        
        # FILETYPE / COUNTER
        var_file_type = _get_file_type(file)
        if var_file_type:
            counter[var_file_type] += 1
        
        # DIMENSIONS / SELECT
        if var_file_type == 'Image':
            try:
                im = Image.open(os.path.join(PATH_SERVER, path, file))
                var_image_dimensions = im.size
            except:
                # if image is corrupt, change filetype to not defined
                var_file_type = ''
            # check, if image is generated with ImageGenerator
            var_image_version = _is_image_version(file)
            if var_image_version == False:
                results_var['imagegenerator_total'] += 1
                
        # MAKETHUMB (thumbnails might be uploaded/generated for any file type)
        try:
            thumb = Image.open(os.path.join(PATH_SERVER, path, "_cache", THUMB_PREFIX + file + ".png"))
            var_thumb_dimensions = thumb.size
            var_path_thumb = "%s%s_cache/%s%s.png" % (URL_WWW, path, THUMB_PREFIX, file)
        except:
            if var_file_type == 'Image':
                # if thumbnail does not exist, show makethumb-Icon instead.
                var_path_thumb = URL_FILEBROWSER_MEDIA + 'img/filebrowser_Thumb.gif'
                var_flag_makethumb = True
        
        # FILTER / SEARCH
        flag_extend = False
        if query['filter_type'] != '' and query['filter_date'] != '' and var_file_type == query['filter_type'] and _get_filterdate(query['filter_date'], date_time):
            flag_extend = True
        elif query['filter_type'] != '' and query['filter_date'] == '' and var_file_type == query['filter_type']:
            flag_extend = True
        elif query['filter_type'] == '' and query['filter_date'] != '' and _get_filterdate(query['filter_date'], date_time):
            flag_extend = True
        elif query['filter_type'] == '' and query['filter_date'] == '':
            flag_extend = True
        if query['q'] and not re.compile(query['q'].lower(), re.M).search(file.lower()):
            flag_extend = False
            
        # DATABASE FILE OBJECT
        var_file_obj, is_created = File.objects.get_or_create(
            path=not dir_name and file or dir_name+'/'+file,
            defaults={
                'size': var_filesize_long,
                'width': var_image_dimensions and var_image_dimensions[0] or None,
                'height': var_image_dimensions and var_image_dimensions[1] or None,
                'file_type': var_file_type,
                'uploaded': var_date,
                }
            )
        # APPEND FILE_LIST
        if flag_extend == True:
            file_info = SortedDict(( # the order matters
                ('filename', file),                           #  0
                ('filesize_long', var_filesize_long),         #  1
                ('filesize_str', var_file_obj.get_filesize()),#  2
                ('date', var_date),                           #  3
                ('path_thumb', var_path_thumb),               #  4
                ('link', var_link),                           #  5
                ('select_link', var_select_link),             #  6
                ('file_extension', var_file_extension),       #  7
                ('file_type', var_file_type),                 #  8
                ('image_dimensions', var_image_dimensions),   #  9
                ('thumb_dimensions', var_thumb_dimensions),   # 10
                ('filename_lower', file.lower()),             # 11
                ('flag_makethumb', var_flag_makethumb),       # 12
                ('flag_deletedir', var_flag_deletedir),       # 13
                ('flag_imageversion', var_image_version),     # 14
                ('obj', var_file_obj),                        # 15
                ('uploader', unicode(var_file_obj.uploader)), # 16
                ))
            file_list.append(file_info)
    
    # SORT LIST
    file_list.sort(lambda x, y: cmp(
        x.value_for_index(int(query['o'])),
        y.value_for_index(int(query['o'])),
        ))
    if query['ot'] == "desc":
       file_list.reverse()
    
    # RESULTS
    results_var['results_current'] = len(file_list)
    for file in file_list:
        if file['file_type'] == 'Image':
            results_var['change_total'] += 1
        if file['file_type'] != 'Folder':
            results_var['delete_total'] += 1
        elif file['file_type'] == 'Folder' and file['flag_deletedir'] == True:
            results_var['delete_total'] += 1
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'file_list': file_list,
        'results_var': results_var,
        'query': query,
        'counter': counter,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, ''),
        'title': _('FileBrowser'),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
index = staff_member_required(never_cache(index))


def mkdir(request, dir_name=None):
    """
    Make directory
    """
    if not request.user.has_perm("filebrowser.make_dir"):
        t = loader.get_template("403.html")
        return HttpResponseForbidden(t.render(RequestContext(request)))

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
        'root_path': URL_HOME,
    }, context_instance=Context(request))
mkdir = staff_member_required(never_cache(mkdir))


def upload(request, dir_name=""):
    """
    Multipe Upload.
    """
    if not request.user.has_perm("filebrowser.add_file"):
        t = loader.get_template("403.html")
        return HttpResponseForbidden(t.render(RequestContext(request)))
    
    from django.forms.formsets import formset_factory
    
    path = _get_path(dir_name)
    abs_path = os.path.join(PATH_SERVER, dir_name) 
    query = _get_query(request.GET)
    to_replace = re.compile(r'[^a-zA-Z0-9\.-]+') # characters to replace with "_"
    
    # PIL's Error "Suspension not allowed here" work around:
    # s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
    import ImageFile
    ImageFile.MAXBLOCK = IMAGE_MAXBLOCK # default is 64k
    
    UploadFormSet = formset_factory(UploadForm, formset=BaseUploadFormSet, extra=5)
    if request.method == 'POST':
        form = UploadSettingsForm(data=request.POST, files=request.FILES)
        formset = UploadFormSet(data=request.POST, files=request.FILES, path_server=PATH_SERVER, path=path)
        if form.is_valid() and formset.is_valid():
            cleaned = form.cleaned_data
            rename_to_timestamp = cleaned['rename_to_timestamp']
            overwrite_existing = cleaned['overwrite_existing']
            extract_archives = cleaned['extract_archives']
            convert_to_lower_case = cleaned['convert_to_lower_case']
            change_spaces_to_underscores = cleaned['change_spaces_to_underscores']
            image_modifications = cleaned['image_modifications']
            for cleaned_data in formset.cleaned_data:
                if cleaned_data:
                    # UPLOAD FILE
                    media_file = {
                        'uploaded_file': cleaned_data['file'],
                        'title': cleaned_data['title'],
                        'description': cleaned_data['description'],
                        'uploader': request.user,
                        }
                    filename = media_file['uploaded_file'].name
                    if change_spaces_to_underscores:
                        filename = to_replace.sub("_", filename)
                    if convert_to_lower_case:
                        filename = filename.lower()
                    extension = ""
                    if "." in filename:
                        extension = filename[filename.rindex(".")+1:]
    
                    if extension.lower() == "zip" and extract_archives:
                        #archive = zipfile.ZipFile(StringIO(media_file['uploaded_file'].data.read()))
                        archive = zipfile.ZipFile(media_file['uploaded_file'])
                        if archive.testzip():
                            request.user.message_set.create(
                                message=_("The archive '%s' was skipped because it's corrupted.") % media_file['uploaded_file'].filename,
                                )
                            continue
                            
                        for original_filename in archive.namelist():
                            if not original_filename.startswith('__'):
                                content = archive.read(original_filename)
                                if len(content):
                                    filename = original_filename
                                    if change_spaces_to_underscores:
                                        filename = to_replace.sub("_", filename)
                                    if convert_to_lower_case:
                                        filename = filename.lower()
                                    extension = ""
                                    if "." in filename:
                                        extension = filename[filename.rindex(".")+1:]
                                    
                                    if rename_to_timestamp:
                                        filename = datetime.now().strftime("%Y%m%d%H%M%S")
                                        if extension:
                                            filename += "." + extension
                                            
                                    if not overwrite_existing:
                                        filename_without_ext = filename
                                        if extension:
                                            filename_without_ext = filename[:-len(extension) - 1]
                                        i = 2
                                        while os.path.isfile(os.path.join(abs_path, filename)):
                                            if rename_to_timestamp:
                                                time.sleep(1)
                                                filename = datetime.now().strftime("%Y%m%d%H%M%S")
                                            else:
                                                filename = "%s_%d" % (filename_without_ext, i)
                                                i += 1
                                            if extension:
                                                filename += "." + extension
                    
                                    for k, v in EXTENSIONS.iteritems():
                                        for ext in v:
                                            if ext == "." + extension:
                                                file_type = k
                    
                                    if not file_type:
                                        request.user.message_set.create(
                                            message=_("The file '%s' was skipped because it's type is not allowed.") % original_filename,
                                            )
                                    else:
                                        media_file_path = os.path.join(path, filename)
                                        
                                        file_obj = File.objects.save_file(
                                            media_file_path,
                                            content,
                                            **media_file
                                            )

                                        if file_obj.file_type == "Image":
                                            for mod in image_modifications:
                                                modified_path(media_file_path, mod.sysname)

                                        request.user.message_set.create(
                                            message=_("The file '%(oldfilename)s' was successfully uploaded as '%(newfilename)s'.") % {
                                                'oldfilename': original_filename,
                                                'newfilename': filename,
                                            },
                                            )
                                        
                                        if rename_to_timestamp:
                                            time.sleep(1)
                        archive.close()
                        
                    else:
    
                        if rename_to_timestamp:
                            filename = datetime.now().strftime("%Y%m%d%H%M%S")
                            if extension:
                                filename += "." + extension
                        if not overwrite_existing:
                            filename_without_ext = filename
                            if extension:
                                filename_without_ext = filename[:-len(extension) - 1]
                            i = 2
                            while os.path.isfile(os.path.join(abs_path, filename)):
                                if rename_to_timestamp:
                                    time.sleep(1)
                                    filename = datetime.now().strftime("%Y%m%d%H%M%S")
                                else:
                                    filename = "%s_%d" % (filename_without_ext, i)
                                    i += 1
                                if extension:
                                    filename += "." + extension
        
                        media_file_path = os.path.join(path, filename)
    
                        file_obj = File.objects.save_file(
                            media_file_path,
                            media_file['uploaded_file'],
                            **media_file
                            )
                        
                        if file_obj.file_type == "Image":
                            for mod in image_modifications:
                                modified_path(media_file_path, mod.sysname)
                        
                        request.user.message_set.create(
                            message=_("The file '%(oldfilename)s' was successfully uploaded as '%(newfilename)s'.") % {
                                'oldfilename': media_file['uploaded_file'].name,
                                'newfilename': filename,
                            },
                            )
                        
                        if rename_to_timestamp:
                            time.sleep(1)
                    
            # MESSAGE & REDIRECT
            msg = _('Upload successful.')
            request.user.message_set.create(message=msg)
            # on redirect, sort by date desc to see the uploaded files on top of the list
            redirect_url = URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop']
            return HttpResponseRedirect(redirect_url)
    else:
        form = UploadSettingsForm()
        formset = UploadFormSet(path_server=PATH_SERVER, path=path)
    
    return render_to_response('filebrowser/upload.html', {
        'form': form,
        'formset': formset,
        'dir': dir_name,
        'query': _get_query(request.GET),
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, 'Multiple Upload'),
        'title': _('Select files to upload'),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
upload = staff_member_required(never_cache(upload))


def makethumb(request, dir_name=None, file_name=None):
    """
    Make Thumbnail(s) for existing Image or Directory
        This is useful if someone uploads images via FTP, not using the
        upload functionality of the FileBrowser.
        
    The thumbnails will be located at
    <original_dir> + "_cache/" + <original_filename> + ".png"
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
            if os.path.isfile(os.path.join(PATH_SERVER, path, file)) and not os.path.isfile(os.path.join(PATH_SERVER, path, "_cache", THUMB_PREFIX + file)) and not re.compile(THUMB_PREFIX, re.M).search(file) and _get_file_type(file) == "Image":
                _make_image_thumbnail(PATH_SERVER, path, file)
    
    # MESSAGE & REDIRECT
    msg = _('Thumbnail creation successful.')
    request.user.message_set.create(message=msg)
    return HttpResponseRedirect(URL_ADMIN + path + query['query_str_total'])
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'query': query,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, ''),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
makethumb = staff_member_required(never_cache(makethumb))


def delete(request, dir_name=""):
    """
    Delete existing File/Directory.
        If file is an Image, also delete thumbnail.
        When trying to delete a directory, the directory has to be empty.
    """
    if not request.user.has_perm("filebrowser.delete_file"):
        t = loader.get_template("403.html")
        return HttpResponseForbidden(t.render(RequestContext(request)))
        
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    msg = ""
    
    if request.GET:
        server_path = os.path.join(PATH_SERVER, path, request.GET.get('filename'))
        try:
            File.objects.delete_file(not dir_name and request.GET.get('filename') or dir_name + "/" + request.GET.get('filename'))
            
            # MESSAGE & REDIRECT
            msg = _('The file %s was successfully deleted.') % (request.GET.get('filename').lower())
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect(URL_ADMIN + path + query['query_nodelete'])
        except OSError, (errno, strerror):
            msg = strerror
    
    if msg:
        request.user.message_set.create(message=msg)
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'file': request.GET.get('filename', ''),
        'query': query,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, ''),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
delete = staff_member_required(never_cache(delete))


def change(request, dir_name="", file_name=""):
    """
    change database settings and image versions for File/Directory.
    """
    if not request.user.has_perm("filebrowser.change_file"):
        t = loader.get_template("403.html")
        return HttpResponseForbidden(t.render(RequestContext(request)))
    
    path = _get_path(dir_name)
    query = _get_query(request.GET)
    
    if os.path.isfile(os.path.join(PATH_SERVER, path, file_name)): # file
        file_type = _get_file_type(file_name)
        file_extension = os.path.splitext(file_name)[1].lower()
    else:
        file_extension = ""
        file_type = ""
    
    # all file objects should be created either by upload or by file listing
    try:
        file_obj = File.objects.get(
            path=not dir_name and file_name or dir_name + '/' + file_name
            )
    except File.DoesNotExist:
        return HttpResponseRedirect(URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop'])
    
    if request.method == 'POST':
        form = ChangeForm(instance=file_obj, data=request.POST)
        if form.is_valid():
            old_path = os.path.join(PATH_SERVER, path, file_name)
            new_path = os.path.join(PATH_SERVER, path, form.cleaned_data['name'] + file_extension)
            #try:
            if True:
                file_obj = form.save(commit=False)
                if old_path != new_path:
                    os.rename(old_path, new_path)
                    file_obj.path = path + form.cleaned_data['name'] + file_extension
                file_obj.save()
                
                # RENAME THUMBNAILS
                old_thumb_path = os.path.join(PATH_SERVER, path, "_cache", THUMB_PREFIX + file_name + ".png")
                if os.path.isfile(old_thumb_path):
                    new_thumb_path = os.path.join(PATH_SERVER, path, "_cache", THUMB_PREFIX + form.cleaned_data['name'] + file_extension + ".png")
                    try:
                        os.rename(old_thumb_path, new_thumb_path)
                    except OSError, (errno, strerror):
                        form.errors['name'] = forms.util.ErrorList([strerror])
                
                # IMAGE VERSIONS
                if file_obj.file_type == "Image":
                    if old_path != new_path:
                        # delete old image versions
                        for mod_file_path in locate(
                            "%s_*" % file_name,
                            os.path.join(PATH_SERVER, path, "_cache"),
                            ):
                            os.unlink(mod_file_path)
                    # create requested image versions
                    for mod in form.cleaned_data['image_modifications']:
                        modified_path(file_obj.path, mod.sysname)
                
                # MESSAGE & REDIRECT
                if not form.errors:
                    msg = _('Change was successful.')
                    request.user.message_set.create(message=msg)
                    # on redirect, sort by date desc to see the new stuff on top of the list
                    return HttpResponseRedirect(URL_ADMIN + path + "?&ot=desc&o=3&" + query['pop'])
            #except OSError, (errno, strerror):
            #    form.errors['name'] = forms.util.ErrorList([_('Error.')])
    else:
        image_modifications = []
        for img_mod in ImageModification.objects.all():
            if os.path.isfile(img_mod.modified_path(os.path.join(PATH_SERVER, file_obj.path))):
                image_modifications.append(img_mod.pk)
        form = ChangeForm(
            instance=file_obj,
            initial={
                'name': os.path.splitext(file_name)[0],
                'image_modifications': image_modifications,
                },
            )
    return render_to_response('filebrowser/change.html', {
        'form': form,
        'file_obj': file_obj,
        'query': query,
        'file_extension': file_extension,
        'settings_var': _get_settings_var(request.META['HTTP_HOST'], path),
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, 'Change File Properties'),
        'title': _('Change Properties for "%s"') % file_name,
        'root_path': URL_HOME,
    }, context_instance=Context(request))
change = staff_member_required(never_cache(change))

def rename(request, dir_name=None, file_name=None):
    """
    Rename existing File/Directory.
    """
    if not request.user.has_perm("filebrowser.change_file"):
        t = loader.get_template("403.html")
        return HttpResponseForbidden(t.render(RequestContext(request)))
    
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
                    old_thumb_path = os.path.join(PATH_SERVER, path, "_cache", THUMB_PREFIX + file_name)
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
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, 'Rename'),
        'title': _('Rename "%s"') % file_name,
        'root_path': URL_HOME,
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
        'breadcrumbs': _get_breadcrumbs(_get_query(request.GET), dir_name, ''),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
makethumb = staff_member_required(never_cache(makethumb))

def direct_to_js_template(request, cache=True, *args, **kwargs):
    response = direct_to_template(request, *args, **kwargs)
    response['Content-Type'] = "application/x-javascript"
    if cache:
        #response['Cache-Control'] = "max-age=2678400" # cached for one month
        now = datetime.utcnow()
        response['Last-Modified'] = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        expires = now + timedelta(0, 2678400)
        response['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    else:
        response['Pragma'] = "No-Cache"
    return response

def get_or_create_modified_path(request):
    retval = ""
    if request.POST:
        file_path = request.POST.get('file_path', "")
        absolute_path = False
        if file_path.startswith(URL_WWW):
            absolute_path = True
            file_path = file_path[len(URL_WWW):]
        mod_sysname = request.POST.get('mod_sysname', "")
        retval = modified_path(file_path, mod_sysname)
        if retval and absolute_path:
            retval = URL_WWW + retval
    response = HttpResponse(retval)
    response['Content-Type'] = "application/x-javascript"
    response['Pragma'] = "No-Cache"
    return response

