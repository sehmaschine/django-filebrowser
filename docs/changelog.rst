:tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _changelog:

Changelog
=========

3.6.2 (not yet released)
------------------------

3.6.1 (September 9th, 2015)
---------------------------

* Compatibility with Django 1.8 and Grappelli 2.7
* The setting ``VERSIONS_BASEDIR`` is now ``_versions`` by default.
* The settings ``MEDIA_ROOT`` and ``MEDIA_URL`` have been removed.
* File listing is not being filtered if ``VERSIONS_BASEDIR`` is being used.
* Removed ``Folder`` from ``EXTENSIONS``.
