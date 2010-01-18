# coding: utf-8
import os, re

from django.shortcuts import render_to_response, HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext as Context
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from django.dispatch import Signal
try:
    # django SVN
    from django.views.decorators.csrf import csrf_exempt
except:
    # django 1.1
    from django.contrib.csrf.middleware import csrf_exempt

from filebrowser.settings import *
from filebrowser.upload_frontends.uploadify.decorators import flash_login_required
from filebrowser.functions import convert_filename, handle_file_upload, get_path, get_breadcrumbs, get_settings_var
from filebrowser.templatetags.fb_tags import query_helper
from filebrowser.base import FileObject

def upload(request):
    """
    Multipe File Upload.
    """
    
    from django.http import parse_cookie
    
    # QUERY / PATH CHECK
    query = request.GET
    path = get_path(query.get('dir', ''))
    if path is None:
        msg = _('The requested Folder does not exist.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect(reverse("fb_browse"))
    abs_path = os.path.join(MEDIA_ROOT, DIRECTORY, path)
    
    # SESSION (used for flash-uploading)
    cookie_dict = parse_cookie(request.META.get('HTTP_COOKIE', ''))
    engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    session_key = cookie_dict.get(settings.SESSION_COOKIE_NAME, None)
    
    return render_to_response('filebrowser/upload_frontends/uploadify/upload.html', {
        'query': query,
        'get_query': request.GET.urlencode(),
        'title': _(u'Select files to upload'),
        'settings_var': get_settings_var(),
        'session_key': session_key,
        'breadcrumbs': get_breadcrumbs(query, path),
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
    fb_uploadurl_re = re.compile(r'^(%s)' % reverse("fb_upload"))
    folder = fb_uploadurl_re.sub('', folder)
    
    fileArray = {}
    if request.method == 'POST':
        for k,v in request.POST.items():
            if k != "folder":
                v = convert_filename(v)
                if os.path.isfile(os.path.join(MEDIA_ROOT, DIRECTORY, folder, v)):
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
        fb_uploadurl_re = re.compile(r'^(%s)' % reverse("fb_upload"))
        folder = fb_uploadurl_re.sub('', folder)
        abs_path = os.path.join(MEDIA_ROOT, DIRECTORY, folder)
        if request.FILES:
            filedata = request.FILES['Filedata']
            filedata.name = convert_filename(filedata.name)
            # PRE UPLOAD SIGNAL
            filebrowser_pre_upload.send(sender=request, path=request.POST.get('folder'), file=filedata)
            # HANDLE UPLOAD
            uploadedfile = handle_file_upload(abs_path, filedata)
            # MOVE UPLOADED FILE
            # if file already exists
            if os.path.isfile(os.path.join(MEDIA_ROOT, DIRECTORY, folder, filedata.name)):
                old_file = os.path.join(abs_path, filedata.name)
                new_file = os.path.join(abs_path, uploadedfile)
                file_move_safe(new_file, old_file)
            # POST UPLOAD SIGNAL
            filebrowser_post_upload.send(sender=request, path=request.POST.get('folder'), file=FileObject(os.path.join(DIRECTORY, folder, filedata.name)))
    return HttpResponse('True')
