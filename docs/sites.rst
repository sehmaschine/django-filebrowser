:tocdepth: 2

.. |site| replace:: FileBrowser site
.. |sites| replace:: FileBrowser sites

.. _sites:

FileBrowser Sites
=================

.. versionadded:: 3.4

As of version 3.4, FileBrowser application is respresented by an object of the ``filebrowser.sites.FileBrowserSite`` class (in analogy to the Django's admin site). FileBrowser sites allow you to:

	- associate custom actions (analogy to Django's admin actions) to a site,

	- subclass from FileBrowserSite and redefine the default FileBrowser's behavior,

	- and to use multiple FileBrowser sites in your project.

The module variable ``site`` from filebrowser.sites is the default FileBrowser application.

Backward Incompatibilites
-------------------------

The only thing that you need to pay attention to when migrating to FileBrowser 3.4, is the specification of your URL-patterns. URL-patterns are now associated with a FileBrowser site, that is, each FileBrowser site can have different URL-patterns. See :ref:`quickstart` for how to setup your URL-patterns.


Mutliple FileBrowser Sites
--------------------------

.. important::
	
	In majority of cases, there's no need for seting up multiple instances of FileBrowser sites. It is a supported, but not very standard way of using FileBrowser. However, there might be a few good reasons to use multiple |sites|. For example, you want to allow users to upload/delete/modify files at a location outside MEDIA_ROOT or you have implemented some custom actions that should be accessible only to certain users. In these cases, having multiple |sites| can do the job.

Before you start including additional FileBrowser sites to your project, note that there will be always a **single** FileBrowser site associated with FileBrowseFields. This site, called the **main site**, is invoked, when a user clicks on the search button of a FieldBrowseField. If you use multiple |sites|, then the main site is the one with the instance namespace "filebrowser" (or the last deployed instance, if there is no instance named "filebrowser").

When creating a site, you can specify its instance namespace like this::

	fb_site = FileBrowserSite(name="fb-site")

The default |site| ``filebrowser.sites.site`` has the instance name "filebrowser" and will be therefore the main site if you use it.

The Main Site
^^^^^^^^^^^^^

Although it is possible to define MEDIA_ROOT and MEDIA_URL on per-site basis, the main site *must* have these variables equal to the global, default values given in ``settings.py``. See :ref:`settings` for the details about MEDIA_ROOT and MEDIA_URL.

Additional Sites
^^^^^^^^^^^^^^^^

Any site, that is not the main site can have its MEDIA_ROOT and MEDIA_URL set to a whatever value you wish. In order to deploy an additional |site|, create the instance and give it a unique name::

	fb_site = FileBrowserSite(name="fb-site")

set its MEDIA_ROOT and MEDIA_URL::

	fb_site.media_root = '/usr/var/www/some-project/ohter-media/'
	fb_site.media_url = 'other-media/'

and register the site's URLs in your ``url.py``::

	from some_project import fb_site
	
	urlpatterns = patterns('',
            (r'^admin/filebrowser-other-media/', include(fb_site.urls)),
)






