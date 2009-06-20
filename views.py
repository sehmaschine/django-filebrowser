# coding: utf-8

import os, string, ftplib, re, decimal
from time import gmtime, strftime, localtime, mktime, time

from django.shortcuts import render_to_response
from django.template import RequestContext as Context
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings
from django import forms

# get settings
from filebrowser.fb_settings import *
# get functions
from filebrowser.functions import _sort_by_attr, _get_path, _get_subdir_list, _get_dir_list, _get_breadcrumbs, _get_filterdate,_get_settings_var, _handle_file_upload, _get_file_type, _image_generator, _image_crop_generator, _is_image_version, _url_join, _is_selectable
from filebrowser.templatetags.fb_tags import query_helper
# get forms
from filebrowser.forms import MakeDirForm, RenameForm, UploadForm, BaseUploadFormSet

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image

# Precompile regular expressions
filter_re = [ re.compile(THUMB_PREFIX, re.M) ]
for exp in EXCLUDE:
    filter_re.append(re.compile(exp))
    

class FileObject(object):
    def __init__(self, filename, path, selecttype=None):
        self.filename = filename
        self.filename_lower = filename.lower() # important for sorting
        self.path = path
        self.filesize = os.path.getsize(os.path.join(PATH_SERVER, path, filename))
        self.date = os.path.getmtime(os.path.join(PATH_SERVER, path, filename))
        self.filetype = _get_file_type(filename)
        if not selecttype or self.filetype in SELECT_FORMATS[selecttype.capitalize()]:
            self.selectable = True
    
    def _filetype_checked(self):
        if self.filetype == "Folder" and os.path.isdir(self.path_full()):
            return self.filetype
        elif self.filetype != "Folder" and os.path.isfile(self.path_full()):
            return self.filetype
        else:
            return ""
    filetype_checked = property(_filetype_checked)
    
    def icon_url(self):
        icon = "filebrowser_type_" + self.filetype_checked.lower() + ".gif"
        return u"%s%s" % (_url_join(URL_FILEBROWSER_MEDIA, "img"), icon)
    
    def path_full(self):
        return u"%s" % os.path.join(PATH_SERVER, self.path, self.filename)
    
    def path_relative(self):
        return u"%s" % self.path_full().replace(settings.MEDIA_ROOT, '').lstrip('/')
    
    def url_full(self):
        if self.filetype == "Folder":
            return u"%s" % _url_join(URL_WWW, self.path, self.filename)
        else:
            return u"%s%s" % (_url_join(URL_WWW, self.path), self.filename)
    
    def url_relative(self):
        return u"%s" % self.url_full().replace(settings.MEDIA_URL, '').lstrip('/')
    
    def url_save(self):
        if SAVE_FULL_URL:
            return self.url_full()
        else:
            return self.url_relative()
    
    def link(self):
        if self.filetype_checked == "Folder":
            return u"%s%s" % (_url_join(URL_ADMIN, self.path), self.filename)
        else:
            return u"%s%s" % (_url_join(URL_WWW, self.path), self.filename)
    
    def date_formatted(self):
        return u"%s" % strftime("%Y-%m-%d", gmtime(self.date))
        
    def image_dimensions(self):
        if self.filetype == 'Image':
            try:
                im = Image.open(os.path.join(PATH_SERVER, path, self.filename))
                return im.size
            except:
                pass
        else:
            return False
    
    def image_is_generated(self):
        if self.filetype == 'Image':
            return _is_image_version(self.filename)
        else:
            return False
    
    def folder_is_empty(self):
        if os.path.isdir(self.path_full()):
            if not os.listdir(self.path_full()):
                return True
            else:
                return False
        else:
            return False
    
    def thumbnail_size(self):
        return THUMBNAIL_SIZE
    

def index(request, dir_name=None):
    """
    Show list of files on a server-directory.
    """
    
    path = _get_path(dir_name)
    query = request.GET
    
    # INITIAL VARIABLES
    results_var = {'results_total': 0, 'results_current': 0, 'delete_total': 0, 'thumbs_total': 0, 'generator_total': 0, 'select_total': 0 }
    counter = {}
    for k,v in EXTENSIONS.iteritems():
        counter[k] = 0
    
    dir_list = os.listdir(os.path.join(PATH_SERVER, path))
    files = []
    for file in dir_list:
        
        # EXCLUDE FILES MATCHING THUMB_PREFIX OR ANY OF THE EXCLUDE PATTERNS
        filtered = file.startswith('.')
        for re_prefix in filter_re:
            if re_prefix.search(file):
                filtered = True
        if filtered:
            continue
        # only increment results_total if file is not filtered
        results_var['results_total'] += 1
        
        # CREATE FILEOBJECT
        fileobject = FileObject(file, path, request.GET.get('type', ''))
        
        # COUNTER/RESULTS
        if fileobject.filetype:
            counter[fileobject.filetype] += 1
        if fileobject.filetype == 'Image' and fileobject.image_is_generated() == False:
            results_var['generator_total'] += 1
        if fileobject.filetype == 'Image':
            results_var['thumbs_total'] += 1
        if fileobject.filetype != 'Folder':
            results_var['delete_total'] += 1
        elif fileobject.filetype == 'Folder' and fileobject.folder_is_empty():
            results_var['delete_total'] += 1
        
        # FILTER / SEARCH
        append = False
        if fileobject.filetype == request.GET.get('filter_type', fileobject.filetype) and _get_filterdate(request.GET.get('filter_date', ''), fileobject.date):
            append = True
        if request.GET.get('q') and not re.compile(request.GET.get('q').lower(), re.M).search(file.lower()):
            append = False
        
        # APPEND FILE_LIST
        if append:
            files.append(fileobject)
            results_var['results_current'] += 1
    
    # SORTING
    files = _sort_by_attr(files, request.GET.get('o', 'date'))
    if request.GET.get('ot') == "desc":
        files.reverse()
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'files': files,
        'results_var': results_var,
        'query': query,
        'counter': counter,
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, dir_name, ''),
        'title': _(u'FileBrowser'),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
index = staff_member_required(never_cache(index))


def mkdir(request, dir_name=None):
    """
    Make directory
    """
    
    path = _get_path(dir_name)
    query = request.GET
    
    if request.method == 'POST':
        form = MakeDirForm(PATH_SERVER, path, request.POST)
        if form.is_valid():
            server_path = os.path.join(PATH_SERVER, path, form.cleaned_data['dir_name'].lower())
            try:
                os.mkdir(server_path)
                os.chmod(server_path, 0775)
                # MESSAGE & REDIRECT
                msg = _('The Folder %s was successfully created.') % (form.cleaned_data['dir_name'].lower())
                request.user.message_set.create(message=msg)
                # on redirect, sort by date desc to see the new directory on top of the list
                # remove filter in order to actually _see_ the new folder
                return HttpResponseRedirect(URL_ADMIN + path + query_helper(query, "ot=desc,o=date", "ot,o,filter_type,filter_data"))
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
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, dir_name, _(u'New Folder')),
        'title': _(u'New Folder'),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
mkdir = staff_member_required(never_cache(mkdir))


def upload(request, dir_name=None):
    """
    Multipe Upload.
    """
    
    from django.forms.formsets import formset_factory
    
    path = _get_path(dir_name)
    query = request.GET
    
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
    
    UploadFormSet = formset_factory(UploadForm, formset=BaseUploadFormSet, extra=5)
    if request.method == 'POST':
        formset = UploadFormSet(data=request.POST, files=request.FILES, path_server=PATH_SERVER, path=path)
        if formset.is_valid():
            for cleaned_data in formset.cleaned_data:
                if cleaned_data:
                    # UPLOAD FILE
                    _handle_file_upload(PATH_SERVER, path, cleaned_data['file'])
                    if _get_file_type(cleaned_data['file'].name) == "Image":
                        # IMAGE GENERATOR
                        if FORCE_GENERATOR or (cleaned_data['use_image_generator'] and (IMAGE_GENERATOR_LANDSCAPE != "" or IMAGE_GENERATOR_PORTRAIT != "")):
                            _image_generator(PATH_SERVER, path, cleaned_data['file'].name)
                        # GENERATE CROPPED/RECTANGULAR IMAGE
                        if FORCE_GENERATOR or (cleaned_data['use_image_generator'] and IMAGE_CROP_GENERATOR != ""):
                            _image_crop_generator(PATH_SERVER, path, cleaned_data['file'].name)
            # MESSAGE & REDIRECT
            msg = _('Upload successful.')
            request.user.message_set.create(message=msg)
            # on redirect, sort by date desc to see the uploaded files on top of the list
            # remove filter in order to actually _see_ the uploaded file(s)
            return HttpResponseRedirect(URL_ADMIN + path + query_helper(query, "ot=desc,o=date", "ot,o,filter_type,filter_data"))
    else:
        formset = UploadFormSet(path_server=PATH_SERVER, path=path)
    
    return render_to_response('filebrowser/upload.html', {
        'formset': formset,
        'dir': dir_name,
        'query': query,
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, dir_name, _(u'Upload')),
        'title': _(u'Select files to upload'),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
upload = staff_member_required(never_cache(upload))


def delete(request, dir_name=None):
    """
    Delete existing File/Directory.
        When trying to delete a directory, the directory has to be empty.
    """
    
    path = _get_path(dir_name)
    query = request.GET
    msg = ""
    
    if request.GET:
        if request.GET.get('filetype') != "Folder":
            server_path = os.path.join(PATH_SERVER, path, request.GET.get('filename'))
            try:
                # DELETE FILE
                os.unlink(server_path)
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
                return HttpResponseRedirect(URL_ADMIN + path + query_helper(query, "", "filename,filetype"))
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
                return HttpResponseRedirect(URL_ADMIN + path + query_helper(query, "", "filename,filetype"))
            except OSError:
                # todo: define error message
                msg = OSError
    
    if msg:
        request.user.message_set.create(message=msg)
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'file': request.GET.get('filename', ''),
        'query': query,
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, dir_name, ''),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
delete = staff_member_required(never_cache(delete))


def rename(request, dir_name=None, file_name=None):
    """
    Rename existing File/Directory.
    """
    
    path = _get_path(dir_name)
    query = request.GET
    
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
                # RENAME IMAGE VERSIONS? TOO MUCH MAGIC?
                
                # MESSAGE & REDIRECT
                msg = _('Renaming was successful.')
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect(URL_ADMIN + path + query_helper(query, "", ""))
            except OSError, (errno, strerror):
                form.errors['name'] = forms.util.ErrorList([_('Error.')])
    else:
        form = RenameForm(PATH_SERVER, path, file_extension)
    
    return render_to_response('filebrowser/rename.html', {
        'form': form,
        'query': query,
        'file_extension': file_extension,
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, dir_name, _(u'Rename')),
        'title': _(u'Rename "%s"') % file_name,
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
    query = request.GET
    
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
            if os.path.isfile(os.path.join(PATH_SERVER, path, file)) and _get_file_type(file) == "Image":
                # GENERATE IMAGES
                if IMAGE_GENERATOR_LANDSCAPE != "" or IMAGE_GENERATOR_PORTRAIT != "":
                    _image_generator(PATH_SERVER, path, file)
                # GENERATE CROPPED/RECTANGULAR IMAGE
                if IMAGE_CROP_GENERATOR != "":
                    _image_crop_generator(PATH_SERVER, path, file)
    
    # MESSAGE & REDIRECT
    msg = _('Successfully generated Images.')
    request.user.message_set.create(message=msg)
    return HttpResponseRedirect(URL_ADMIN + path + query_helper(query, "", ""))
    
    return render_to_response('filebrowser/index.html', {
        'dir': dir_name,
        'query': query,
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, dir_name, ''),
        'root_path': URL_HOME,
    }, context_instance=Context(request))
generateimages = staff_member_required(never_cache(generateimages))


