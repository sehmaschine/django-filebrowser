# coding: utf-8

# django imports
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.template import RequestContext
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured

# filebrowser imports
from filebrowser.functions import get_path, get_file
from filebrowser.templatetags.fb_tags import query_helper


def flash_login_required(function):
    """
    Decorator to recognize a user by its session.
    Used for Flash-Uploading.
    """
    
    def decorator(request, *args, **kwargs):
        try:
            engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        except:
            import django.contrib.sessions.backends.db
            engine = django.contrib.sessions.backends.db
        session_data = engine.SessionStore(request.POST.get('session_key'))
        user_id = session_data['_auth_user_id']
        # will return 404 if the session ID does not resolve to a valid user
        request.user = get_object_or_404(User, pk=user_id)
        return function(request, *args, **kwargs)
    return decorator


def path_exists(function):
    """
    Check if the given path exists.
    """
    
    def decorator(request, *args, **kwargs):
        if get_path('') == None:
            # The DIRECTORY does not exist, raise an error to prevent eternal redirecting.
            raise ImproperlyConfigured, _("Error finding Upload-Folder (MEDIA_ROOT + DIRECTORY). Maybe it does not exist?")
        if get_path(request.GET.get('dir', '')) == None:
            msg = _('The requested Folder does not exist.')
            messages.add_message(request, messages.ERROR, msg)
            redirect_url = reverse("fb_browse") + query_helper(request.GET, "", "dir")
            return HttpResponseRedirect(redirect_url)
        return function(request, *args, **kwargs)
    return decorator


def file_exists(function):
    """
    Check if the given file exists.
    """
    
    def decorator(request, *args, **kwargs):
        if get_file(request.GET.get('dir', ''), request.GET.get('filename', '')) == None:
            msg = _('The requested File does not exist.')
            messages.add_message(request, messages.ERROR, msg)
            redirect_url = reverse("fb_browse") + query_helper(request.GET, "", "dir")
            return HttpResponseRedirect(redirect_url)
        return function(request, *args, **kwargs)
    return decorator


