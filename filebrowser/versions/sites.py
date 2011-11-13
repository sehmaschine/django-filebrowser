# coding: utf-8

# PYTHON IMPORTS
import os, re
from types import MethodType

# DJANGO IMPORTS
from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext as Context
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext as _
from django import forms
from django.core.urlresolvers import reverse, get_urlconf, get_resolver
from django.dispatch import Signal
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.encoding import smart_unicode
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, FileSystemStorage
from django.core.exceptions import ImproperlyConfigured

# FILEBROWSER IMPORTS
from filebrowser.templatetags.fb_tags import query_helper
from filebrowser.decorators import path_exists, file_exists
from filebrowser.storage import FileSystemStorageMixin, StorageMixin
from filebrowser.sites import FileBrowserSite
from filebrowser.base import FileListing
from filebrowser.versions.base import VersionFileObject
from filebrowser.versions.functions import get_breadcrumbs, get_filterdate, handle_file_upload, convert_filename
from filebrowser.versions.settings import *

# Add some required methods to FileSystemStorage
if FileSystemStorageMixin not in FileSystemStorage.__bases__:
    FileSystemStorage.__bases__ += (FileSystemStorageMixin,)

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image

# JSON import
try:
    import json
except ImportError:
    from django.utils import simplejson as json


class VersionFileBrowserSite(FileBrowserSite):
    
    file_class = VersionFileObject

    def _get_settings_var(self, directory):
        settings_var = super(VersionFileBrowserSite, self)._get_settings_var(directory)
        # Versions
        settings_var['VERSIONS_BASEDIR'] = VERSIONS_BASEDIR
        settings_var['VERSIONS'] = VERSIONS
        settings_var['ADMIN_VERSIONS'] = ADMIN_VERSIONS
        settings_var['ADMIN_THUMBNAIL'] = ADMIN_THUMBNAIL
        return settings_var

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include
        
        urlpatterns = super(VersionFileBrowserSite, self).get_urls()        
        urlpatterns += patterns('',
            url(r'^version/$', file_exists(self, path_exists(self, self.filebrowser_view(self.version))), name="fb_version"),
        )

        return urlpatterns
    
    def _get_filter_regex(self):
        filter_re = super(VersionFileBrowserSite, self)._get_filter_regex()
        for k,v in VERSIONS.iteritems():
            exp = (r'_%s(%s)') % (k, '|'.join(EXTENSION_LIST))
            filter_re.append(re.compile(exp))
        return filter_re

    def _delete_versions(self, fileobject, **kwargs):
        fileobject.delete_versions()
        
    def delete(self, request):
        self.filebrowser_during_delete.connect(self._delete_versions)
        return super(VersionFileBrowserSite, self).delete(request)
        
    def browse(self, request, template='filebrowser/versions/index.html',
        header_template='filebrowser/versions/include/tableheader.html',
        item_template='filebrowser/versions/include/filelisting.html'):
        return super(VersionFileBrowserSite, self).browse(request, template,
            header_template, item_template)

    def detail(self, request, template='filebrowser/versions/detail.html'):
        """
        Show detail page for a file.
        
        Rename existing File/Directory. Also deletes existing Image Versions/Thumbnails.
        """

        self.filebrowser_during_rename.connect(self._delete_versions)
        return super(VersionFileBrowserSite, self).detail(request, template)

    def version(self, request, template='filebrowser/versions/version.html'):
        """
        Version detail.
        """
        query = request.GET
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))
        fileobject = self.file_class(os.path.join(path, query.get('filename', '')), site=self)
        
        return render_to_response(template, {
            'fileobject': fileobject,
            'query': query,
            'settings_var': self._get_settings_var(directory=self.directory),
            'site': self
        }, context_instance=Context(request, current_app=self.name))


# Default FileBrowser site
site = VersionFileBrowserSite(name='filebrowser')

# Default actions
from actions import *
site.add_action(flip_horizontal)
site.add_action(flip_vertical)
site.add_action(rotate_90_clockwise)
site.add_action(rotate_90_counterclockwise)
site.add_action(rotate_180)


