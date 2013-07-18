:tocdepth: 2

.. |site| replace:: FileBrowser site
.. |sites| replace:: FileBrowser sites

.. _sites:

FileBrowser Sites
=================

.. versionadded:: 3.4.0

As of version 3.4, the FileBrowser application is respresented by an object of ``filebrowser.sites.FileBrowserSite`` (in analogy to Django's admin site). FileBrowser sites allow you to:

	- associate :ref:`actions` (analogy to Django's admin actions) to a site,
	- define a *file system storage* for a site (allows for browsing remote file servers) -- see :ref:`storages`,
	- subclass from FileBrowserSite and redefine the default FileBrowser's behavior,
	- use multiple FileBrowser sites in your project.

The module variable ``site`` from filebrowser.sites is the default FileBrowser application.

Backward Incompatibilites
-------------------------

The only thing that you need to pay attention to when migrating to FileBrowser 3.4 is the specification of your URL–patterns. URL–patterns are now associated with a FileBrowser site, that is, each FileBrowser site can have different URL–patterns.

See :ref:`quickstart` for how to setup your URL–patterns.