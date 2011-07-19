:tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _releasenotes:

FileBrowser 3.3 Release Notes
=============================

FileBrowser 3.3 is compatible with Django 1.3 and Grappelli 2.3.

Overview
^^^^^^^^

* Compatibility with Staticfiles.
* Compatibility with the new messages framework.
* Consistent use of absolute paths (including ``MEDIA_ROOT`` and ``DIRECTORY`` settings).
* Reworked and simplified ``base.py``, ``views.py`` and ``functions.py``.
* Updated to Uploadify 2.1.4.
* Translation is done with Transifex.
* Added Tests.

What's new in FileBrowser 3.3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Added class ``FileListing``.
* Added attributes ``mimetype``, ``is_original``, ``is_version`` and ``versions`` to ``FileObject``.
* Added widgets ``FileInput``, ``ClearableFileInput``.
* Settings ``SEARCH_TRAVERSE``.
* Translations are handled with Transifex.
* Added Tests.
* Added edit-view.
* Easier selection of Files (for either the FileBrowseField or the Rich-Text-Editor).
* Added delete-confirmation.
* Image transpose (flip, rotate).
* Added setting ``FB_DEFAULT_PERMISSIONS``.

Design changes
^^^^^^^^^^^^^^

* The button for renaming/deleting a File/Folder is no longer part of the changelist.
* Instead, there is now an edit-button.
* The edit-view allows for renaming/deleting a File/Folder (similar to editing a database-object with the admin-interface).
* Selecting a File/Folder is done with one button on the changelist with a drop-down for ``VERSIONS``.
* Versions are now shown with the change-link/edit-view.

Deprecated in 3.3
^^^^^^^^^^^^^^^^^

* DEBUG-setting.
* Removed attribute ``url_thumbnail`` from ``FileObject``, because this should be done with versions.
* Removed the extensions for code (js, css, ...) from the default settings since these files should not be stored within ``MEDIA_ROOT``.
* Removed rename-view (this is now part of the edit-view).
