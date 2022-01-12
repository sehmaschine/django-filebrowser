.. Django FileBrowser documentation master file, created by
   sphinx-quickstart on Sun Dec  5 19:11:46 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

Django FileBrowser Documentation
================================

**Media-Management with Grappelli**.

.. note::
    |filebrowser| 4.0 requires Django 4.0 and |grappelli| 3.0.

Installation and Setup
----------------------

.. toctree::
   :maxdepth: 3

   quickstart
   settings

API
---

.. toctree::
   :maxdepth: 4

   api

Fields & Widgets
----------------

.. toctree::
   :maxdepth: 3

   fieldswidgets

Admin Interface
---------------

.. toctree::
   :maxdepth: 3

   admin

Image Versions
--------------

.. toctree::
   :maxdepth: 3

   versions

Help
----

.. toctree::
   :maxdepth: 2

   help
   testing
   changelog

Main Features
-------------

* Browse your media files with the admin interface.
* Multiple upload, including a progress bar.
* Automatic thumbnails.
* Image versions to fit your websites grid (esp. useful with adaptive/responsive layouts).
* Integration with TinyMCE.
* FileBrowseField to select images/documents.
* Signals for upload, rename and delete.
* Custom actions.
* Custom file storage engines.

Code
----

https://github.com/sehmaschine/django-filebrowser

Discussion
----------

Use the `FileBrowser Google Group <http://groups.google.com/group/django-filebrowser>`_ to ask questions or discuss features.

Versions and Compatibility
--------------------------

**FileBrowser is always developed against the latest stable Django release and is NOT tested with Djangos trunk.**

* FileBrowser 4.0.1 (January 12th, 2022): Compatible with Django 4.0
* FileBrowser 3.14.3 (January 12th, 2022): Compatible with Django 3.2 (LTS)

Current development branches:

* FileBrowser 4.0.2 (Development Version for Django 4.0, see Branch Stable/4.0.x)
* FileBrowser 3.14.4 (Development Version for Django 3.2, see Branch Stable/3.14.x)

Older versions are available at GitHub, but are not supported anymore.
