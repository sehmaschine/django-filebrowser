:tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _releasenotes:

FileBrowser 3.4 Release Notes
=============================

FileBrowser 3.4 is compatible with Django 1.3 and Grappelli 2.3.

Overview
^^^^^^^^

With version 3.4 of the FileBrowser, the code has been moved to GitHub. We did a major code cleanup and the performance has been improved. Custom actions have been added and the flash-based uploader has been replaced with an ajax-uploader.

Upgrading from 3.3.0
^^^^^^^^^^^^^^^^^^^^^

Due to the new FileBrowser sites, adding the filebrowser url-pattern has changed compared with previous versions.

Instead of::

	urlpatterns = patterns('',
    	(r'^admin/filebrowser/', include('filebrowser.urls')),
	)

you now need to define the urls like this::

    from filebrowser.sites import site
    
    urlpatterns = patterns('',
       url(r'^admin/filebrowser/', include(site.urls)),
    )

What's new in FileBrowser 3.4
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Added FileBrowser sites.
* Added site-based storage engines.
* Added custom actions.
* Added widget ``FileInput``.
* Added ``methods`` argument to versions.
* Added ``placeholder``.
* Replaced the flash-based upload with an ajax-based uploader (thanks to Steve Losh).

Deprecated in 3.4
^^^^^^^^^^^^^^^^^

* Removed flash-based upload with Uploadify.
* Removed ``SAVE_FULL_URL``.
