# coding: utf-8

# general imports
import itertools, os, re
from time import gmtime, strftime

# django imports
from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext as Context
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from django.conf import settings
from django import forms
from django.core.urlresolvers import reverse
from django.dispatch import Signal
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.encoding import smart_str
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

# filebrowser imports
from filebrowser.settings import *
from filebrowser.functions import get_breadcrumbs, get_filterdate, get_settings_var, handle_file_upload, convert_filename
from filebrowser.templatetags.fb_tags import query_helper
from filebrowser.base import FileListing, FileObject
from filebrowser.decorators import flash_login_required, path_exists, file_exists

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image

# CHOICES
TRANSPOSE_CHOICES = (
    ("0", u"-----"),
    ("1", Image.FLIP_LEFT_RIGHT),
    ("2", Image.FLIP_TOP_BOTTOM),
    ("3", Image.ROTATE_90),
    ("4", Image.ROTATE_180),
    ("5", Image.ROTATE_270),
)

filter_re = []
for exp in EXCLUDE:
   filter_re.append(re.compile(exp))
for k,v in VERSIONS.iteritems():
    exp = (r'_%s(%s)') % (k, '|'.join(EXTENSION_LIST))
    filter_re.append(re.compile(exp))

def filter_browse(item):
    filtered = item.filename.startswith('.')
    for re_prefix in filter_re:
        if re_prefix.search(item.filename):
            filtered = True
    if filtered:
        return False
    return True


@path_exists
def browse(request):
    """
    Browse Files/Directories.
    """
    
    query = request.GET.copy()
    abs_path = u'%s' % os.path.join(MEDIA_ROOT, DIRECTORY, query.get('dir', ''))
    filelisting = FileListing(abs_path,
        filter_func=filter_browse,
        sorting_by=query.get('o', DEFAULT_SORTING_BY),
        sorting_order=query.get('ot', DEFAULT_SORTING_ORDER))
    
    files = []
    if SEARCH_TRAVERSE and query.get("q"):
        listing = filelisting.files_walk_filtered()
    else:
        listing = filelisting.files_listing_filtered()
    for fileobject in listing:
        # date/type filter
        append = False
        if fileobject.filetype == query.get('filter_type', fileobject.filetype) and get_filterdate(query.get('filter_date', ''), fileobject.date or 0):
            append = True
        # search
        if query.get("q") and not re.compile(query.get("q").lower(), re.M).search(fileobject.filename.lower()):
            append = False
        # append
        if append:
            files.append(fileobject)
    filelisting.results_total = filelisting.results_listing_filtered
    filelisting.results_current = len(files)
    
    p = Paginator(files, LIST_PER_PAGE)
    page_nr = request.GET.get('p', '1')
    try:
        page = p.page(page_nr)
    except (EmptyPage, InvalidPage):
        page = p.page(p.num_pages)
    
    return render_to_response('filebrowser/index.html', {
        'p': p,
        'page': page,
        'filelisting': filelisting,
        'query': query,
        'title': _(u'FileBrowser'),
        'settings_var': get_settings_var(),
        'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
        'breadcrumbs_title': ""
    }, context_instance=Context(request))
browse = staff_member_required(never_cache(browse))


# mkdir signals
filebrowser_pre_createdir = Signal(providing_args=["path", "name"])
filebrowser_post_createdir = Signal(providing_args=["path", "name"])

@path_exists
def createdir(request):
    """
    Create Directory.
    """
    from filebrowser.forms import CreateDirForm
    query = request.GET
    abs_path = u'%s' % os.path.join(MEDIA_ROOT, DIRECTORY, query.get('dir', ''))
    
    if request.method == 'POST':
        form = CreateDirForm(abs_path, request.POST)
        if form.is_valid():
            abs_server_path = os.path.join(abs_path, form.cleaned_data['name'])
            try:
                filebrowser_pre_createdir.send(sender=request, path=abs_server_path, name=form.cleaned_data['name'])
                os.mkdir(abs_server_path)
                os.chmod(abs_server_path, 0775) # ??? PERMISSIONS
                filebrowser_post_createdir.send(sender=request, path=abs_server_path, name=form.cleaned_data['name'])
                messages.add_message(request, messages.SUCCESS, _('The Folder %s was successfully created.') % form.cleaned_data['name'])
                redirect_url = reverse("fb_browse") + query_helper(query, "ot=desc,o=date", "ot,o,filter_type,filter_date,q,p")
                return HttpResponseRedirect(redirect_url)
            except OSError, (errno, strerror):
                if errno == 13:
                    form.errors['name'] = forms.util.ErrorList([_('Permission denied.')])
                else:
                    form.errors['name'] = forms.util.ErrorList([_('Error creating folder.')])
    else:
        form = CreateDirForm(abs_path)
    
    return render_to_response('filebrowser/createdir.html', {
        'form': form,
        'query': query,
        'title': _(u'New Folder'),
        'settings_var': get_settings_var(),
        'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
        'breadcrumbs_title': _(u'New Folder')
    }, context_instance=Context(request))
createdir = staff_member_required(never_cache(createdir))


@path_exists
def upload(request):
    """
    Multipe File Upload.
    """
    from django.http import parse_cookie
    query = request.GET
    abs_path = u'%s' % os.path.join(MEDIA_ROOT, DIRECTORY, query.get('dir', ''))
    
    # SESSION (used for flash-uploading)
    cookie_dict = parse_cookie(request.META.get('HTTP_COOKIE', ''))
    engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    session_key = cookie_dict.get(settings.SESSION_COOKIE_NAME, None)
    
    return render_to_response('filebrowser/upload.html', {
        'session_key': session_key,
        'query': query,
        'title': _(u'Select files to upload'),
        'settings_var': get_settings_var(),
        'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
        'breadcrumbs_title': _(u'Upload')
    }, context_instance=Context(request))
upload = staff_member_required(never_cache(upload))


@csrf_exempt
def _check_file(request):
    """
    Check if file already exists on the server.
    """
    from django.utils import simplejson
    
    folder = request.POST.get('folder')
    fb_uploadurl_re = re.compile(r'^.*(%s)' % reverse("fb_upload"))
    folder = fb_uploadurl_re.sub('', folder)
    
    fileArray = {}
    if request.method == 'POST':
        for k,v in request.POST.items():
            if k != "folder":
                v = convert_filename(v)
                if os.path.isfile(smart_str(os.path.join(MEDIA_ROOT, DIRECTORY, folder, v))):
                    fileArray[k] = v
    
    return HttpResponse(simplejson.dumps(fileArray))


# upload signals
filebrowser_pre_upload = Signal(providing_args=["path", "file"])
filebrowser_post_upload = Signal(providing_args=["path", "file"])

@csrf_exempt
@flash_login_required
def _upload_file(request):
    """
    Upload file to the server.
    """
    from django.core.files.move import file_move_safe
    
    if request.method == 'POST':
        folder = request.POST.get('folder')
        fb_uploadurl_re = re.compile(r'^.*(%s)' % reverse("fb_upload"))
        folder = fb_uploadurl_re.sub('', folder)
        abs_path = os.path.join(MEDIA_ROOT, DIRECTORY, folder)
        if request.FILES:
            filedata = request.FILES['Filedata']
            filedata.name = convert_filename(filedata.name)
            filebrowser_pre_upload.send(sender=request, path=request.POST.get('folder'), file=filedata)
            uploadedfile = handle_file_upload(abs_path, filedata)
            # if file already exists
            if os.path.isfile(smart_str(os.path.join(MEDIA_ROOT, DIRECTORY, folder, filedata.name))):
                old_file = smart_str(os.path.join(abs_path, filedata.name))
                new_file = smart_str(os.path.join(abs_path, uploadedfile))
                file_move_safe(new_file, old_file, allow_overwrite=True)
            # POST UPLOAD SIGNAL
            filebrowser_post_upload.send(sender=request, path=request.POST.get('folder'), file=FileObject(smart_str(os.path.join(DIRECTORY, folder, filedata.name))))
    return HttpResponse('True')
#_upload_file = flash_login_required(_upload_file)


@path_exists
@file_exists
def delete_confirm(request):
    """
    Delete existing File/Directory.
    """
    query = request.GET
    abs_path = u'%s' % os.path.join(MEDIA_ROOT, DIRECTORY, query.get('dir', ''))
    fileobject = FileObject(os.path.join(abs_path, query.get('filename', '')))
    if fileobject.filetype == "Folder":
        filelisting = FileListing(os.path.join(abs_path, fileobject.filename),
            filter_func=filter_browse,
            sorting_by=query.get('o', 'filename'),
            sorting_order=query.get('ot', DEFAULT_SORTING_ORDER))
        filelisting = filelisting.files_walk_total()
        if len(filelisting) > 100:
            additional_files = len(filelisting) - 100
            filelisting = filelisting[:100]
        else:
            additional_files = None
    else:
        filelisting = None
        additional_files = None
    
    return render_to_response('filebrowser/delete_confirm.html', {
        'fileobject': fileobject,
        'filelisting': filelisting,
        'additional_files': additional_files,
        'query': query,
        'title': _(u'Confirm delete'),
        'settings_var': get_settings_var(),
        'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
        'breadcrumbs_title': _(u'Confirm delete')
    }, context_instance=Context(request))
delete_confirm = staff_member_required(never_cache(delete_confirm))


# delete signals
filebrowser_pre_delete = Signal(providing_args=["path", "name"])
filebrowser_post_delete = Signal(providing_args=["path", "name"])

@path_exists
@file_exists
def delete(request):
    """
    Delete existing File/Directory.
    When trying to delete a Directory, the Directory has to be empty.
    """
    query = request.GET
    abs_path = u'%s' % os.path.join(MEDIA_ROOT, DIRECTORY, query.get('dir', ''))
    fileobject = FileObject(os.path.join(abs_path, query.get('filename', '')))
    
    if request.GET:
        try:
            filebrowser_pre_delete.send(sender=request, path=fileobject.path, name=fileobject.filename)
            fileobject.delete_versions()
            fileobject.delete()
            filebrowser_post_delete.send(sender=request, path=fileobject.path, name=fileobject.filename)
            messages.add_message(request, messages.SUCCESS, _('Successfully deleted %s') % fileobject.filename)
        except OSError, (errno, strerror):
            # TODO: define error-message
            pass
    redirect_url = reverse("fb_browse") + query_helper(query, "", "filename,filetype")
    return HttpResponseRedirect(redirect_url)
delete = staff_member_required(never_cache(delete))


# rename signals
filebrowser_pre_rename = Signal(providing_args=["path", "name", "new_name"])
filebrowser_post_rename = Signal(providing_args=["path", "name", "new_name"])

@path_exists
@file_exists
def detail(request):
    """
    Show detail page for a file.
    
    Rename existing File/Directory (deletes existing Image Versions/Thumbnails).
    """
    from filebrowser.forms import ChangeForm
    query = request.GET
    abs_path = u'%s' % os.path.join(MEDIA_ROOT, DIRECTORY, query.get('dir', ''))
    fileobject = FileObject(os.path.join(abs_path, query.get('filename', '')))
    
    if request.method == 'POST':
        form = ChangeForm(request.POST, path=abs_path, fileobject=fileobject)
        if form.is_valid():
            new_name = form.cleaned_data['name']
            transpose = form.cleaned_data['transpose']
            try:
                if new_name != fileobject.filename:
                    filebrowser_pre_rename.send(sender=request, path=fileobject.path, name=fileobject.filename, new_name=new_name)
                    fileobject.delete_versions()
                    os.rename(fileobject.path, os.path.join(fileobject.head, new_name))
                    filebrowser_post_rename.send(sender=request, path=fileobject.path, name=fileobject.filename, new_name=new_name)
                    messages.add_message(request, messages.SUCCESS, _('Renaming was successful.'))
                if transpose:
                    im = Image.open(fileobject.path)
                    new_image = im.transpose(int(transpose))
                    try:
                        new_image.save(fileobject.path, quality=VERSION_QUALITY, optimize=(os.path.splitext(fileobject.path)[1].lower() != '.gif'))
                    except IOError:
                        new_image.save(fileobject.path, quality=VERSION_QUALITY)
                    fileobject.delete_versions()
                    messages.add_message(request, messages.SUCCESS, _('Transposing was successful.'))
                if "_continue" in request.POST:
                    redirect_url = reverse("fb_detail") + query_helper(query, "filename="+new_name, "filename")
                else:
                    redirect_url = reverse("fb_browse") + query_helper(query, "", "filename")
                return HttpResponseRedirect(redirect_url)
            except OSError, (errno, strerror):
                form.errors['name'] = forms.util.ErrorList([_('Error.')])
    else:
        form = ChangeForm(initial={"name": fileobject.filename}, path=abs_path, fileobject=fileobject)
    
    return render_to_response('filebrowser/detail.html', {
        'form': form,
        'fileobject': fileobject,
        'query': query,
        'title': u'%s' % fileobject.filename,
        'settings_var': get_settings_var(),
        'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
        'breadcrumbs_title': u'%s' % fileobject.filename
    }, context_instance=Context(request))
detail = staff_member_required(never_cache(detail))


@path_exists
@file_exists
def version(request):
    """
    Version detail.
    """
    query = request.GET
    abs_path = u'%s' % os.path.join(MEDIA_ROOT, DIRECTORY, query.get('dir', ''))
    fileobject = FileObject(os.path.join(abs_path, query.get('filename', '')))
    
    return render_to_response('filebrowser/version.html', {
        'fileobject': fileobject,
        'query': query,
        'settings_var': get_settings_var(),
    }, context_instance=Context(request))
version = staff_member_required(never_cache(version))


