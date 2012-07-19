:tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _changelog:

Changelog
=========

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