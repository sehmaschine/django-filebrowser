# coding: utf-8

import os, re
from time import gmtime, strftime

from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext as Context
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from django.conf import settings
from django import forms
from django.core.urlresolvers import reverse

# filebrowser imports
from filebrowser.fb_settings import *
from filebrowser.functions import _url_to_path, _path_to_url, _sort_by_attr, _get_path, _get_file, _get_version_path, _get_breadcrumbs, _get_filterdate, _get_settings_var, _handle_file_upload, _get_file_type, _url_join
from filebrowser.templatetags.fb_tags import query_helper
from filebrowser.base import FileObject

# Precompile regular expressions
filter_re = []
for exp in EXCLUDE:
   filter_re.append(re.compile(exp))
for k,v in VERSIONS.iteritems():
    exp = (r'_%s.(jpg|png|gif)') % k
    filter_re.append(re.compile(exp))
    

def browse(request):
    """
    Browse Files/Directories.
    """
    
    # QUERY / PATH CHECK
    query = request.GET
    path = _get_path(query.get('dir', ''))
    if path is None:
        msg = _('Directory/File does not exist.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(reverse("fb_browse"))
    abs_path = os.path.join(settings.MEDIA_ROOT, DIRECTORY, path)
    
    # INITIAL VARIABLES
    results_var = {'results_total': 0, 'results_current': 0, 'delete_total': 0, 'images_total': 0, 'select_total': 0 }
    counter = {}
    for k,v in EXTENSIONS.iteritems():
        counter[k] = 0
    
    dir_list = os.listdir(abs_path)
    files = []
    for file in dir_list:
        
        # EXCLUDE FILES MATCHING VERSIONS_PREFIX OR ANY OF THE EXCLUDE PATTERNS
        filtered = file.startswith('.')
        for re_prefix in filter_re:
            if re_prefix.search(file):
                filtered = True
        if filtered:
            continue
        results_var['results_total'] += 1
        
        # CREATE FILEOBJECT
        fileobject = FileObject(os.path.join(DIRECTORY, path, file))
        
        # COUNTER/RESULTS
        if fileobject.filetype:
            counter[fileobject.filetype] += 1
        if fileobject.filetype == 'Image':
            results_var['images_total'] += 1
        if fileobject.filetype != 'Folder':
            results_var['delete_total'] += 1
        elif fileobject.filetype == 'Folder' and fileobject.is_empty:
            results_var['delete_total'] += 1
        if query.get('type') and query.get('type') in SELECT_FORMATS and fileobject.filetype in SELECT_FORMATS[query.get('type')]:
            results_var['select_total'] += 1
        elif not query.get('type'):
            results_var['select_total'] += 1
        
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
        'dir': path,
        'files': files,
        'results_var': results_var,
        'counter': counter,
        'query': query,
        'title': _(u'FileBrowser'),
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, path, ''),
    }, context_instance=Context(request))
browse = staff_member_required(never_cache(browse))


def mkdir(request):
    """
    Make Directory.
    """
    
    from filebrowser.forms import MakeDirForm
    
    # QUERY / PATH CHECK
    query = request.GET
    path = _get_path(query.get('dir', ''))
    if path is None:
        msg = _('Directory/File does not exist.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(reverse("fb_browse"))
    abs_path = os.path.join(settings.MEDIA_ROOT, DIRECTORY, path)
    
    if request.method == 'POST':
        form = MakeDirForm(abs_path, request.POST)
        if form.is_valid():
            server_path = os.path.join(abs_path, form.cleaned_data['dir_name'].lower())
            try:
                os.mkdir(server_path)
                os.chmod(server_path, 0775)
                msg = _('The Folder %s was successfully created.') % (form.cleaned_data['dir_name'].lower())
                request.user.message_set.create(message=msg)
                # on redirect, sort by date desc to see the new directory on top of the list
                # remove filter in order to actually _see_ the new folder
                redirect_url = reverse("fb_browse") + query_helper(query, "ot=desc,o=date", "ot,o,filter_type,filter_date,q")
                return HttpResponseRedirect(redirect_url)
            except OSError, (errno, strerror):
                if errno == 13:
                    form.errors['dir_name'] = forms.util.ErrorList([_('Permission denied.')])
                else:
                    form.errors['dir_name'] = forms.util.ErrorList([_('Error creating directory.')])
    else:
        form = MakeDirForm(abs_path)
    
    return render_to_response('filebrowser/makedir.html', {
        'form': form,
        'query': query,
        'title': _(u'New Folder'),
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, path, _(u'New Folder')),
    }, context_instance=Context(request))
mkdir = staff_member_required(never_cache(mkdir))


def upload(request):
    """
    Multipe File Upload.
    """
    
    # QUERY / PATH CHECK
    query = request.GET
    path = _get_path(query.get('dir', ''))
    if path is None:
        msg = _('Directory/File does not exist.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(reverse("fb_browse"))
    abs_path = os.path.join(MEDIA_ROOT, DIRECTORY, path)
    
    return render_to_response('filebrowser/upload.html', {
        'query': query,
        'title': _(u'Select files to upload'),
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, path, _(u'Upload')),
    }, context_instance=Context(request))
upload = staff_member_required(never_cache(upload))


def _check_file(request):
    """
    Check if file already exists on the server.
    """
    
    from django.utils import simplejson
    
    folder = request.POST.get('folder')
    fb_uploadurl_re = re.compile(r'^(%s)' % reverse("fb_upload"))
    folder = fb_uploadurl_re.sub('', folder)
    
    fileArray = {}
    if request.method == 'POST':
        for k,v in request.POST.items():
            if k != "folder":
                if os.path.isfile(os.path.join(MEDIA_ROOT, DIRECTORY, folder, v)):
                    fileArray[k] = v
    
    return HttpResponse(simplejson.dumps(fileArray))


def _upload_file(request):
    """
    Upload file to the server.
    """
    
    from django.core.files.move import file_move_safe
    
    if request.method == 'POST':
        folder = request.POST.get('folder')
        fb_uploadurl_re = re.compile(r'^(%s)' % reverse("fb_upload"))
        folder = fb_uploadurl_re.sub('', folder)
        abs_path = os.path.join(MEDIA_ROOT, DIRECTORY, folder)
        if request.FILES:
            filedata = request.FILES['Filedata']
            uploadedfile = _handle_file_upload(abs_path, filedata)
            if os.path.isfile(os.path.join(MEDIA_ROOT, DIRECTORY, folder, filedata.name)):
                old_file = os.path.join(abs_path, filedata.name)
                new_file = os.path.join(abs_path, uploadedfile)
                file_move_safe(new_file, old_file)
    return HttpResponse(True)


def delete(request):
    """
    Delete existing File/Directory.
    
    When trying to delete a Directory, the Directory has to be empty.
    """
    
    # QUERY / PATH CHECK
    query = request.GET
    path = _get_path(query.get('dir', ''))
    filename = _get_file(query.get('dir', ''), query.get('filename', ''))
    if path is None or filename is None:
        msg = _('Directory/File does not exist.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(reverse("fb_browse"))
    abs_path = os.path.join(settings.MEDIA_ROOT, DIRECTORY, path)
    
    msg = ""
    if request.GET:
        if request.GET.get('filetype') != "Folder":
            relative_server_path = os.path.join(DIRECTORY, path, filename)
            try:
                # DELETE IMAGE VERSIONS/THUMBNAILS
                for version in VERSIONS:
                    try:
                        os.unlink(os.path.join(MEDIA_ROOT, _get_version_path(relative_server_path, version)))
                    except:
                        pass
                # DELETE FILE
                os.unlink(os.path.join(abs_path, filename))
                msg = _('The file %s was successfully deleted.') % (filename.lower())
                request.user.message_set.create(message=msg)
                redirect_url = reverse("fb_browse") + query_helper(query, "", "filename,filetype")
                return HttpResponseRedirect(redirect_url)
            except OSError:
                # todo: define error message
                msg = OSError
        else:
            try:
                os.rmdir(os.path.join(abs_path, filename))
                msg = _('The directory %s was successfully deleted.') % (filename.lower())
                request.user.message_set.create(message=msg)
                redirect_url = reverse("fb_browse") + query_helper(query, "", "filename,filetype")
                return HttpResponseRedirect(redirect_url)
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
    }, context_instance=Context(request))
delete = staff_member_required(never_cache(delete))


def rename(request):
    """
    Rename existing File/Directory.
    
    Includes renaming existing Image Versions/Thumbnails.
    """
    
    from filebrowser.forms import RenameForm
    
    # QUERY / PATH CHECK
    query = request.GET
    path = _get_path(query.get('dir', ''))
    filename = _get_file(query.get('dir', ''), query.get('filename', ''))
    if path is None or filename is None:
        msg = _('Directory/File does not exist.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(reverse("fb_browse"))
    abs_path = os.path.join(settings.MEDIA_ROOT, DIRECTORY, path)
    file_extension = os.path.splitext(filename)[1].lower()
    
    if request.method == 'POST':
        form = RenameForm(abs_path, file_extension, request.POST)
        if form.is_valid():
            relative_server_path = os.path.join(DIRECTORY, path, filename)
            new_relative_server_path = os.path.join(DIRECTORY, path, request.POST.get('name').lower() + file_extension)
            try:
                # DELETE IMAGE VERSIONS/THUMBNAILS
                # regenerating versions/thumbs will be done automatically
                for version in VERSIONS:
                    try:
                        os.unlink(os.path.join(MEDIA_ROOT, _get_version_path(relative_server_path, version)))
                    except:
                        pass
                # RENAME ORIGINAL
                os.rename(os.path.join(MEDIA_ROOT, relative_server_path), os.path.join(MEDIA_ROOT, new_relative_server_path))
                msg = _('Renaming was successful.')
                request.user.message_set.create(message=msg)
                redirect_url = reverse("fb_browse") + query_helper(query, "", "filename")
                return HttpResponseRedirect(redirect_url)
            except OSError, (errno, strerror):
                form.errors['name'] = forms.util.ErrorList([_('Error.')])
    else:
        form = RenameForm(abs_path, file_extension)
    
    return render_to_response('filebrowser/rename.html', {
        'form': form,
        'query': query,
        'file_extension': file_extension,
        'title': _(u'Rename "%s"') % filename,
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, path, _(u'Rename')),
    }, context_instance=Context(request))
rename = staff_member_required(never_cache(rename))


def versions(request):
    """
    Show all Versions for an Image according to ADMIN_VERSIONS.
    """
    
    # QUERY / PATH CHECK
    query = request.GET
    path = _get_path(query.get('dir', ''))
    filename = _get_file(query.get('dir', ''), query.get('filename', ''))
    if path is None or filename is None:
        msg = _('Directory/File does not exist.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(reverse("fb_browse"))
    abs_path = os.path.join(settings.MEDIA_ROOT, DIRECTORY, path)
    
    return render_to_response('filebrowser/versions.html', {
        'original': _path_to_url(os.path.join(DIRECTORY, path, filename)),
        'query': query,
        'title': _(u'Versions for "%s"') % filename,
        'settings_var': _get_settings_var(),
        'breadcrumbs': _get_breadcrumbs(query, path, _(u'Versions for "%s"') % filename),
    }, context_instance=Context(request))
versions = staff_member_required(never_cache(versions))


