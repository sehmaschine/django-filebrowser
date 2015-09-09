:orphan:

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _releasenotes:

FileBrowser 3.6 Release Notes
=============================

FileBrowser 3.6 is compatible with Django 1.8 as well as Grappelli 2.7.

Updates
-------

* Compatibility with Django 1.8 and Grappelli 2.7
* The setting ``VERSIONS_BASEDIR`` is now ``_versions`` by default.
* The settings ``MEDIA_ROOT`` and ``MEDIA_URL`` have been removed.
* File listing is not being filtered if ``VERSIONS_BASEDIR`` is being used.
* Removed ``Folder`` from ``EXTENSIONS``.
* Templatetag ``version`` can now be used as ``version ... as varname`` (instead of ``version_object``).
* New ``FileBrowseUploadField`` (experimental).

Upcoming Depreciations (3.7)
----------------------------

* ``version_object`` will be removed with 3.7
* Defining a ``VERSIONS_BASEDIR`` outside of site.directory will be mandatory with 3.7
* ``FileInput`` and ``ClearableFileInput`` will be removed with 3.7

Update from FileBrowser 3.5.x
-----------------------------

* Update Django to 1.8 and check https://docs.djangoproject.com/en/dev/releases/1.8/
* Update Grappelli to 2.7.x
* Update FileBrowser to 3.6.x
