.. :tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _caching:

Caching of File Listings 
========================

Browsing the contents of directories that contain large number of files can take long seconds. In order to improve responsivness of directory browsing, FileBrowser provides the option to cache file listings of selected directories.


Selecting Directories for Caching 
=================================

It is up to a user to select directories which would benefit from caching. FileBrowser will cache the listings of each directory that contains the file  ``.cached`` (the exact name of this marker file is given by the value of ``CACHE_MARKER_FILENAME`` in ``filebrowser.settings``). The contents of the marker file is never read by FileBrowser.

**Example**
In order to have FileBrowser cache the listing of a directory 'many-files' under ``MEDIA_ROOT``/uploads, create a file '.cached' in that directory by executing::
    
    $touch <MEDIA_ROOT>/uploads/many-files/.cached


What is Cached 
==============

Complete file listings (``base.FileListing`` objects) of selected directories. A file listing of a particular directory contains a list of ``base.FileObject`` objects, each with detail information about files from that directory. 

A *timestamp* marking the creation of a listing is associated with each cache entry (i.e., with each stored ``FileListing`` object).


Cache Updates 
=============

A cached listing of particular directory is considered fresh if the creation time of the listing is newer (bigger) than the modification time of that directory. This way, it is possible to use FTP clients alongside FileBrowser without running into inconsistencies. FileBrowser rebuilds the cached listings from scratch whenever it detects that a listing's timestamp is older than the modification time of an associated directory. Any actions on files that a user excutes via FileBrowser (upload, renaming, etc.) are automatically reflected in the cached data and timestamps are updated accordingly (i.e., the cache is kept up-to-date without the need of rebuilding it from scratch).


How it is Cached
================

There are two options how to cache the data: using a global variable or a Django's cache backend. 

Global Variable
---------------

Using a global variable is the default option and has the best performance for the price of possibly higher memory consumption. However, the amount of required memory depends only on the number of running processes (Django instances) and the number and size of the cached directories. This means, that caching will require a fairly constant amount of memory, assuming that the number of running Django instances and size of cached directories does not change dramatically over time.

Since cached data are stored in a global variable of the module ``cache.py``, cross-process caching is not possible and the cached data are lost by each Django's restart.  Choose this option if you're confident that your http server settings and general requirements are compatible with this kind of caching. 

Django's Cache Backends
-----------------------

If you prefere to use one of Django's cache backends, setup a cache backend called ``filebrowser_cache`` (the exact name is given by the variable ``filebrowser.settings.FILEBROWSER_CACHE_NAME``). Note that using Django's cache backends will not perform as fast as the global-variable option. This is due to the overhead of pickling employed by Django's cache backends. 

See Django's cache documentation on how to setup cache backends. Pay attention to the ``TIMEOUT`` settings and choose an appropriate value -- there is probably no good reason to remove the data from cache at any time and the ``TIMEOUT`` can thus be set to a rather large value (e.g., days, weeks).


Important
=========

FileBrowser should be configured to store image versions in a dedicated directory other than the cached directories. In the opposite case, FileBrowser's on-demand generation of image versions will cause a rebuild of the cached listings any time a new version is generated or old one deleted. See also :ref:`versions` documentation.
