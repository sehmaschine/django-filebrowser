:tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _changelog:

Changelog
=========

3.11.3 (not yet released)
-------------------------

3.11.2 (November 14th, 2019)
----------------------------

* FIXED: updated translations.
* FIXED: allow default string values with `FileBrowseField`.
* FIXED: use empty_values(s) with `FileBrowseField`. Makes sure that the field always returns the expected value.
* FIXED: selecting files based on `SELECT_FORMATS`.
* FIXED: changed admin_static to static, removed Django warning.
* IMPROVED: always show folders with pop-ups.
* IMPROVED: ensure that pillow is processed as a requirement at installation time.
* IMPROVED: support for TinyMCE v4.

3.11.1 (November 2nd, 2018)
---------------------------

* Compatibility with Django 2.1 and Grappelli 2.12

For further information, see :ref:`releasenotes`.
