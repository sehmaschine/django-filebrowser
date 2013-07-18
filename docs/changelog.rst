:tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _changelog:

Changelog
=========

3.5.3 (not yet released)
------------------------

* New: added ``path_full`` to FileObject.
* Improved: added docx to EXTENSIONS.
* Improved: Recommend pillow instead of PIL as a requirement.
* Improved: Added additional test cases.
* Improved: Updated documentation.
* Improved: Consistent use of storage (e.g. storage.location, storage.url).
* Improved: Removed unnecessary functions (e.g. url_join, url_strip).
* Improved: Moved sort_by_attr to FileListing.
* Improved: Regex matches with file versions on browse.
* Improved: Using django.conf.urls (with django.conf.urls.defaults as fallback).
* Improved: Adding CONTRIBUTING.rst.
* Fixed: fixed exception handling with python 2.5.
* Fixed: fixes dir with SEARCH_TRAVERSE true and version select.
* Fixed: Make Django FileUploadHandlers work (also fixed a memory leak).
* Fixed: return correct filename with ``OVERWRITE_EXISTING``.
* Fixed: fb_version_generate with ``FILEBROWSER_VERSIONS_BASEDIR``.

3.5.2 (February 22, 2013)
-------------------------

* Fixed: Use placeholder with version_generate (not only templatetags).
* Fixed: translate extension group name in upload form.
* Fixed: updated filter dropdown HTML.
* Fixed: Make setup.py work with Python 3.
* Fixed: File submit with search traversal.
* Fixed: Fixed fileobject path with Windows.
* Improved: Throwing an exception when in DEBUG and version is not generated (with using the templatetag).
* Compatibility with Django 1.5.

3.5.1 (November 09, 2012)
-------------------------

* Fixed: Documentation with Signals.
* Fixed: File Upload using basic submission.
* Fixed: Added site instance to Signals.
* Improved: Don't hide errors during generate-command.
* Improved: Follow symlinks with generate-command.
* Improved: Added some translations (e.g. for "Upload File").
* New: Setting OVERWRITE_EXISTING.
* New: Added file ``signals.py``.
* New: Support for Django 1.5.

3.5.0 (July 20, 2012)
---------------------

* Compatibility with Django 1.4 and Grappelli 2.4.

3.4.3 (20.6.2012)
-----------------

* Fixed a bug with versions not being generated (in case of capitalized extensions).

3.4.2 (26.3.2012)
-----------------

* Fixed security bug: added staff_member_required decorator to the upload-function.
* Fixed a XSS vulnerability with fb_tags. 

3.4.1 (7.3.2012)
----------------

* Fixed an error with quotes (french translation) in upload.html.
* Updated translations.
* FileObject now returns path (with __unicode__ and __str__), instead of filename. This is needed because otherwise form.has_changed will always be triggerde when using a FileBrowseField.
* Fixed a bug with versions and "f referenced before assignment" (e.g. when an image is being deleted)
* Updated docs (warning that FILEBROWSER_MEDIA_ROOT and FILEBROWSER_MEDIA_URL will be removed with the next major release – use custom storage engine instead).
* Fixed issue with MEDIA_URL hardcoded in tests.
* Fixed issue when MEDIA_URL starts with https://.
* Fixed issue with default-site (if no site is given).
* Fixed bug with using L10N and MAX_UPLOAD_SIZE in upload.html.
* Fixed small bug with importing Http404 in sites.py.
* Fixed bug with Fileobject.exists.
* Added NORMALIZE_FILENAME.

3.4.0 (15/11/2011)
------------------

* Final release of 3.4, see :ref:`releasenotes`