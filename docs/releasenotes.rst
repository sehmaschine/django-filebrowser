:orphan:

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _releasenotes:

FileBrowser 3.7 Release Notes
=============================

FileBrowser 3.7 is compatible with Django 1.9 as well as Grappelli 2.8.

Updates
-------

* Compatibility with Django 1.9 and Grappelli 2.8
* If you use versions, defining a ``VERSIONS_BASEDIR`` outside of site.directory is now mandatory.

Depreciations (3.7)
-------------------

As already noted with 3.6, there's a couple of backwards-incompatible changes with 3.7.

* FileObject ``directory`` is deprecated (use ``path_relative_directory`` instead).
* FileObject ``folder`` is deprecated (use ``dirname`` instead).
* ``FileInput`` and ``ClearableFileInput`` have been removed.
* ``version_object`` has been removed (use ``version`` instead).

Update from FileBrowser 3.6.x
-----------------------------

* Update Django to 1.9 and check https://docs.djangoproject.com/en/dev/releases/1.8/
* Update Grappelli to 2.8.x
* Update FileBrowser to 3.7.x
