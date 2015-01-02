# coding: utf-8

# PYTHON IMPORTS
import os

# DJANGO IMPORTS
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_text

# FILEBROWSER IMPORTS
from filebrowser.templatetags.fb_tags import query_helper


def get_path(path, site=None):
    "Get path."
    if path.startswith('.') or os.path.isabs(path) or not site.storage.isdir(os.path.join(site.directory, path)):
        return None
    return path


def get_file(path, filename, site=None):
    "Get file (or folder)."
    converted_path = smart_text(os.path.join(site.directory, path, filename))
    if not site.storage.isfile(converted_path) and not site.storage.isdir(converted_path):
        return None
    return filename


def path_exists(site, function):
    "Check if the given path exists."

    def decorator(request, *args, **kwargs):
        if get_path('', site=site) is None:
            # The storage location does not exist, raise an error to prevent eternal redirecting.
            raise ImproperlyConfigured(_("Error finding Upload-Folder (site.storage.location + site.directory). Maybe it does not exist?"))
        if get_path(request.GET.get('dir', ''), site=site) is None:
            msg = _('The requested Folder does not exist.')
            messages.add_message(request, messages.ERROR, msg)
            redirect_url = reverse("filebrowser:fb_browse", current_app=site.name) + query_helper(request.GET, u"", "dir")
            return HttpResponseRedirect(redirect_url)
        return function(request, *args, **kwargs)
    return decorator


def file_exists(site, function):
    "Check if the given file exists."

    def decorator(request, *args, **kwargs):
        file_path = get_file(request.GET.get('dir', ''), request.GET.get('filename', ''), site=site)
        if file_path is None:
            msg = _('The requested File does not exist.')
            messages.add_message(request, messages.ERROR, msg)
            redirect_url = reverse("filebrowser:fb_browse", current_app=site.name) + query_helper(request.GET, u"", "dir")
            return HttpResponseRedirect(redirect_url)
        elif file_path.startswith('/') or file_path.startswith('..'):
            # prevent path traversal
            msg = _('You do not have permission to access this file!')
            messages.add_message(request, messages.ERROR, msg)
            redirect_url = reverse("filebrowser:fb_browse", current_app=site.name) + query_helper(request.GET, u"", "dir")
            return HttpResponseRedirect(redirect_url)
        return function(request, *args, **kwargs)
    return decorator
