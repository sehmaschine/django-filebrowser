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
from filebrowser.settings import *
from filebrowser.functions import get_breadcrumbs, get_filterdate, handle_file_upload, convert_filename
from filebrowser.templatetags.fb_tags import query_helper
from filebrowser.base import FileListing, FileObject
from filebrowser.decorators import path_exists, file_exists
from filebrowser.storage import FileSystemStorageMixin, StorageMixin

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

# This cache contains all *instantiated* FileBrowser sites
_sites_cache = {}


def get_site_dict(app_name='filebrowser'):
    """
    Return a dict with all *deployed* FileBrowser sites that have 
    a given app_name.
    """
    if not _sites_cache.has_key(app_name):
        return {}
    # Get names of all deployed filebrowser sites with a give app_name
    deployed = get_resolver(get_urlconf()).app_dict[app_name]
    # Get the deployed subset from the cache
    return dict((k,v) for k, v in _sites_cache[app_name].iteritems() if k in deployed)


def register_site(app_name, site_name, site):
    """
    Add a site into the site dict.
    """
    if not _sites_cache.has_key(app_name):
        _sites_cache[app_name] = {}
    _sites_cache[app_name][site_name] = site


def get_default_site(app_name='filebrowser'):
    """
    Returns the default site. This function uses Django's url resolution method to
    obtain the name of the default site.
    """
    # Get the name of the default site:
    resolver = get_resolver(get_urlconf())
    name = 'filebrowser'

    # Django's default name resolution method (see django.core.urlresolvers.reverse())
    app_list = resolver.app_dict[app_name]
    if not name in app_list:
        name = app_list[0]
    
    return get_site_dict()[name]


class FileBrowserSite(object):
    
    file_class = FileObject

    def __init__(self, name=None, app_name='filebrowser', storage=default_storage):
        self.name = name
        self.app_name = app_name
        self.storage = storage
        
        self._actions = {}
        self._global_actions = self._actions.copy()

        # Register this site in the global site cache
        register_site(self.app_name, self.name, self)
        
        # Per-site settings:
        self.directory = DIRECTORY
        
    def _get_settings_var(self, directory):
        """
        Get settings variables used for FileBrowser listing.
        """
    
        settings_var = {}
        # Main
        settings_var['MEDIA_ROOT'] = MEDIA_ROOT
        settings_var['MEDIA_URL'] = MEDIA_URL
        settings_var['DIRECTORY'] = directory
        # FileBrowser
        settings_var['URL_FILEBROWSER_MEDIA'] = URL_FILEBROWSER_MEDIA
        settings_var['PATH_FILEBROWSER_MEDIA'] = PATH_FILEBROWSER_MEDIA
        # TinyMCE
        settings_var['URL_TINYMCE'] = URL_TINYMCE
        settings_var['PATH_TINYMCE'] = PATH_TINYMCE
        # Extensions/Formats (for FileBrowseField)
        settings_var['EXTENSIONS'] = EXTENSIONS
        settings_var['SELECT_FORMATS'] = SELECT_FORMATS
        # FileBrowser Options
        settings_var['MAX_UPLOAD_SIZE'] = MAX_UPLOAD_SIZE
        # Convert Filenames
        settings_var['CONVERT_FILENAME'] = CONVERT_FILENAME
        # Traverse directories when searching
        settings_var['SEARCH_TRAVERSE'] = SEARCH_TRAVERSE
        return settings_var        
    
    def _directory_get(self):
        return self._directory
    
    def _directory_set(self, val):
        if os.path.basename(val): # There's a trailing slash missing
            raise ImproperlyConfigured("Directory '%(dir)s' for the site %(app_name)s.%(name)s does not end with a trailing slash." % {'dir': val, 'app_name': self.app_name, 'name': self.name})
        if not self.storage.exists(val):
            raise ImproperlyConfigured("Directory '%(dir)s' for the site %(app_name)s.%(name)s does not exist." % {'dir': val, 'app_name': self.app_name, 'name': self.name})
        self._directory = val

    directory = property(_directory_get, _directory_set)

    def filebrowser_view(self, view):
        return staff_member_required(never_cache(view))

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include    

        urlpatterns = patterns('',
    
            # filebrowser urls (views)
            url(r'^browse/$', path_exists(self, self.filebrowser_view(self.browse)), name="fb_browse"),
            url(r'^createdir/', path_exists(self, self.filebrowser_view(self.createdir)), name="fb_createdir"),
            url(r'^upload/', path_exists(self, self.filebrowser_view(self.upload)), name="fb_upload"),
            url(r'^delete_confirm/$', file_exists(self, path_exists(self, self.filebrowser_view(self.delete_confirm))), name="fb_delete_confirm"),
            url(r'^delete/$', file_exists(self, path_exists(self, self.filebrowser_view(self.delete))), name="fb_delete"),
            url(r'^detail/$', file_exists(self, path_exists(self, self.filebrowser_view(self.detail))), name="fb_detail"),
            # non-views
            url(r'^upload_file/$', csrf_exempt(self._upload_file), name="fb_do_upload"),
            
        )

        return urlpatterns

    def _get_filter_regex(self):
        filter_re = []
        for exp in EXCLUDE:
           filter_re.append(re.compile(exp))
        return filter_re

    def add_action(self, action, name=None):
        """
        Register an action to be available globally.
        """
        name = name or action.__name__
        # Check/create short description
        if not hasattr(action, 'short_description'):
            action.short_description = action.__name__.replace("_", " ").capitalize()
        # Check/create applies-to filter
        if not hasattr(action, 'applies_to'):
            action.applies_to = lambda x: True
        self._actions[name] = action
        self._global_actions[name] = action

    def disable_action(self, name):
        """
        Disable a globally-registered action. Raises KeyError for invalid names.
        """
        del self._actions[name]

    def get_action(self, name):
        """
        Explicitally get a registered global action wheather it's enabled or
        not. Raises KeyError for invalid names.
        """
        return self._global_actions[name]

    def applicable_actions(self, fileobject):
        """
        Return a list of tuples (name, action) of actions applicable to a given fileobject.
        """
        res = []
        for name, action in self.actions:
            if action.applies_to(fileobject):
                res.append((name, action))
        return res

    @property
    def actions(self):
        """
        Get all the enabled actions as a list of (name, func). The list
        is sorted alphabetically by actions names
        """
        res = self._actions.items()
        res.sort(key=lambda name_func: name_func[0])
        return res

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name

    def browse(self, request, template='filebrowser/index.html',
        header_template='filebrowser/include/tableheader.html',
        item_template='filebrowser/include/filelisting.html'):
        """
        Browse Files/Directories.
        """

        filter_re = self._get_filter_regex()
        
        def filter_browse(item):
            filtered = item.filename.startswith('.')
            for re_prefix in filter_re:
                if re_prefix.search(item.filename):
                    filtered = True
            if filtered:
                return False
            return True
        
        query = request.GET.copy()
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))
        
        filelisting = FileListing(path,
            filter_func=filter_browse,
            sorting_by=query.get('o', DEFAULT_SORTING_BY),
            sorting_order=query.get('ot', DEFAULT_SORTING_ORDER),
            site=self)
        
        files = []
        if SEARCH_TRAVERSE and query.get("q"):
            listing = filelisting.files_walk_filtered()
        else:
            listing = filelisting.files_listing_filtered()
        
        # If we do a search, precompile the search pattern now
        do_search = query.get("q")
        if do_search:
            re_q = re.compile(query.get("q").lower(), re.M)
        
        filter_type = query.get('filter_type')
        filter_date = query.get('filter_date')
        
        for fileobject in listing:
            # date/type filter
            append = False
            if (not filter_type or fileobject.filetype == filter_type) and (not filter_date or get_filterdate(filter_date, fileobject.date or 0)):
                append = True
            # search
            if do_search and not re_q.search(fileobject.filename.lower()):
                append = False
            # append
            if append:
                files.append(fileobject)
        
        filelisting.results_total = len(listing)
        filelisting.results_current = len(files)
        
        p = Paginator(files, LIST_PER_PAGE)
        page_nr = request.GET.get('p', '1')
        try:
            page = p.page(page_nr)
        except (EmptyPage, InvalidPage):
            page = p.page(p.num_pages)
        
        return render_to_response(template, {
            'p': p,
            'page': page,
            'filelisting': filelisting,
            'query': query,
            'title': _(u'FileBrowser'),
            'settings_var': self._get_settings_var(directory=self.directory),
            'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
            'breadcrumbs_title': "",
            'site': self,
            'header_template': header_template,
            'item_template': item_template,
        }, context_instance=Context(request, current_app=self.name))
    
    # mkdir signals
    filebrowser_pre_createdir = Signal(providing_args=["path", "name"])
    filebrowser_post_createdir = Signal(providing_args=["path", "name"])

    def createdir(self, request, template='filebrowser/createdir.html'):
        """
        Create Directory.
        """
        from filebrowser.forms import CreateDirForm
        query = request.GET
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))
        
        if request.method == 'POST':
            form = CreateDirForm(path, request.POST, site=self)
            if form.is_valid():
                server_path = os.path.join(path, form.cleaned_data['name'])
                try:
                    self.filebrowser_pre_createdir.send(sender=request, path=server_path, name=form.cleaned_data['name'])
                    self.storage.makedirs(server_path)
                    # os.mkdir(server_path)
                    # os.chmod(server_path, 0775) # ??? PERMISSIONS
                    self.filebrowser_post_createdir.send(sender=request, path=server_path, name=form.cleaned_data['name'])
                    messages.add_message(request, messages.SUCCESS, _('The Folder %s was successfully created.') % form.cleaned_data['name'])
                    redirect_url = reverse("filebrowser:fb_browse", current_app=self.name) + query_helper(query, "ot=desc,o=date", "ot,o,filter_type,filter_date,q,p")
                    return HttpResponseRedirect(redirect_url)
                except OSError, (errno, strerror):
                    if errno == 13:
                        form.errors['name'] = forms.util.ErrorList([_('Permission denied.')])
                    else:
                        form.errors['name'] = forms.util.ErrorList([_('Error creating folder.')])
        else:
            form = CreateDirForm(path, site=self)
        
        return render_to_response(template, {
            'form': form,
            'query': query,
            'title': _(u'New Folder'),
            'settings_var': self._get_settings_var(directory=self.directory),
            'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
            'breadcrumbs_title': _(u'New Folder'),
            'site': self
        }, context_instance=Context(request, current_app=self.name))
    

    def upload(self, request, template='filebrowser/upload.html'):
        """
        Multipe File Upload.
        """
        query = request.GET
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))
        
        return render_to_response(template, {
            'query': query,
            'title': _(u'Select files to upload'),
            'settings_var': self._get_settings_var(directory=self.directory),
            'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
            'breadcrumbs_title': _(u'Upload'),
            'site': self
        }, context_instance=Context(request, current_app=self.name))

    def delete_confirm(self, request, template='filebrowser/delete_confirm.html'):
        """
        Delete existing File/Directory.
        """
        query = request.GET
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))
        fileobject = self.file_class(os.path.join(path, query.get('filename', '')), site=self)
        if fileobject.filetype == "Folder":
            filelisting = FileListing(os.path.join(path, fileobject.filename),
                sorting_by=query.get('o', 'filename'),
                sorting_order=query.get('ot', DEFAULT_SORTING_ORDER),
                site=self)
            filelisting = filelisting.files_walk_total()
            if len(filelisting) > 100:
                additional_files = len(filelisting) - 100
                filelisting = filelisting[:100]
            else:
                additional_files = None
        else:
            filelisting = None
            additional_files = None
        
        return render_to_response(template, {
            'fileobject': fileobject,
            'filelisting': filelisting,
            'additional_files': additional_files,
            'query': query,
            'title': _(u'Confirm delete'),
            'settings_var': self._get_settings_var(directory=self.directory),
            'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
            'breadcrumbs_title': _(u'Confirm delete'),
            'site': self
        }, context_instance=Context(request, current_app=self.name))

    # delete signals
    filebrowser_pre_delete = Signal(providing_args=["path", "name"])
    filebrowser_post_delete = Signal(providing_args=["path", "name"])
    # internal use
    filebrowser_during_delete = Signal(providing_args=["fileobject"])

    def delete(self, request):
        """
        Delete existing File/Directory.
        """
        query = request.GET
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))
        fileobject = self.file_class(os.path.join(path, query.get('filename', '')), site=self)
        
        if request.GET:
            try:
                self.filebrowser_pre_delete.send(sender=request, path=fileobject.path, name=fileobject.filename)
                self.filebrowser_during_delete.send(sender=request, fileobject=fileobject)
                fileobject.delete()
                self.filebrowser_post_delete.send(sender=request, path=fileobject.path, name=fileobject.filename)
                messages.add_message(request, messages.SUCCESS, _('Successfully deleted %s') % fileobject.filename)
            # XXX: Can't catch only OSError here, since remote storages won't raise that
            except OSError, (errno, strerror):
                # TODO: define error-message
                pass
        redirect_url = reverse("filebrowser:fb_browse", current_app=self.name) + query_helper(query, "", "filename,filetype")
        return HttpResponseRedirect(redirect_url)

    # rename signals
    filebrowser_pre_rename = Signal(providing_args=["path", "name", "new_name"])
    filebrowser_post_rename = Signal(providing_args=["path", "name", "new_name"])
    # internal use
    filebrowser_during_rename = Signal(providing_args=["fileobject"])

    filebrowser_actions_pre_apply = Signal(providing_args=['action_name', 'fileobjects',])
    filebrowser_actions_post_apply = Signal(providing_args=['action_name', 'filebjects', 'result'])

    def detail(self, request, template='filebrowser/detail.html'):
        """
        Show detail page for a file.
        
        Rename existing File/Directory.
        """
        from filebrowser.forms import ChangeForm
        query = request.GET
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))
        fileobject = self.file_class(os.path.join(path, query.get('filename', '')), site=self)
        
        if request.method == 'POST':
            form = ChangeForm(request.POST, path=path, fileobject=fileobject, site=self)
            if form.is_valid():
                new_name = form.cleaned_data['name']
                action_name = form.cleaned_data['custom_action']
                try:
                    action_response = None
                    if action_name:
                        action = self.get_action(action_name)
                        # Pre-action signal
                        self.filebrowser_actions_pre_apply.send(sender=request, action_name=action_name, fileobject=[fileobject])
                        # Call the action to action
                        action_response = action(request=request, fileobjects=[fileobject])
                        # Post-action signal
                        self.filebrowser_actions_post_apply.send(sender=request, action_name=action_name, fileobject=[fileobject], result=action_response)
                    if new_name != fileobject.filename:
                        self.filebrowser_pre_rename.send(sender=request, path=fileobject.path, name=fileobject.filename, new_name=new_name)
                        self.filebrowser_during_rename.send(sender=request, fileobject=fileobject)
                        self.storage.move(fileobject.path, os.path.join(fileobject.head, new_name))
                        self.filebrowser_post_rename.send(sender=request, path=fileobject.path, name=fileobject.filename, new_name=new_name)
                        messages.add_message(request, messages.SUCCESS, _('Renaming was successful.'))
                    if isinstance(action_response, HttpResponse):
                        return action_response
                    if "_continue" in request.POST:
                        redirect_url = reverse("filebrowser:fb_detail", current_app=self.name) + query_helper(query, "filename="+new_name, "filename")
                    else:
                        redirect_url = reverse("filebrowser:fb_browse", current_app=self.name) + query_helper(query, "", "filename")
                    return HttpResponseRedirect(redirect_url)
                except OSError, (errno, strerror):
                    form.errors['name'] = forms.util.ErrorList([_('Error.')])
        else:
            form = ChangeForm(initial={"name": fileobject.filename}, path=path, fileobject=fileobject, site=self)
        
        return render_to_response(template, {
            'form': form,
            'fileobject': fileobject,
            'query': query,
            'title': u'%s' % fileobject.filename,
            'settings_var': self._get_settings_var(directory=self.directory),
            'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
            'breadcrumbs_title': u'%s' % fileobject.filename,
            'site': self
        }, context_instance=Context(request, current_app=self.name))

    # upload signals
    filebrowser_pre_upload = Signal(providing_args=["path", "file"])
    filebrowser_post_upload = Signal(providing_args=["path", "file"])

    def _upload_file(self, request):
        """
        Upload file to the server.
        """
        if request.method == "POST":
            if request.is_ajax(): # Advanced (AJAX) submission
                folder = request.GET.get('folder')
                filedata = ContentFile(request.raw_post_data)
                try:
                    filedata.name = convert_filename(request.GET['qqfile'])
                except KeyError:
                    return HttpResponseBadRequest('Invalid request! No filename given.')
            else: # Basic (iframe) submission
                # TODO: This needs some attention, do we use this at all?
                folder = request.POST.get('folder')
                if len(request.FILES) == 1:
                    filedata = request.FILES.values()[0]
                else:
                    raise Http404('Invalid request! Multiple files included.')
                # filedata.name = convert_filename(upload.name)
                filedata.name = convert_filename(request.POST.get('file_name'))

            fb_uploadurl_re = re.compile(r'^.*(%s)' % reverse("filebrowser:fb_upload", current_app=self.name))
            folder = fb_uploadurl_re.sub('', folder)

            path = os.path.join(self.directory, folder)
            file_name = os.path.join(path, filedata.name)
            file_already_exists = self.storage.exists(file_name)

            # Check for name collision with a directory
            if file_already_exists and self.storage.isdir(file_name):
                ret_json = {'success': False, 'filename': filedata.name}
                return HttpResponse(json.dumps(ret_json)) 
            
            self.filebrowser_pre_upload.send(sender=request, path=request.POST.get('folder'), file=filedata)
            uploadedfile = handle_file_upload(path, filedata, site=self)
            
            if file_already_exists:
                old_file = smart_unicode(file_name)
                new_file = smart_unicode(uploadedfile)
                self.storage.move(new_file, old_file, allow_overwrite=True)
            
            self.filebrowser_post_upload.send(sender=request, path=request.POST.get('folder'), file=self.file_class(smart_unicode(file_name), site=self))
            
            # let Ajax Upload know whether we saved it or not
            ret_json = {'success': True, 'filename': filedata.name}
            return HttpResponse(json.dumps(ret_json))

# Default FileBrowser site
site = FileBrowserSite(name='filebrowser')
