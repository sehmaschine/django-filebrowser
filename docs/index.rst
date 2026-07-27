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
    |filebrowser| 5.0 requires Django 5.x and |grappelli| 4.x.

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

**FileBrowser is always developed against the latest stable Django release.**

* FileBrowser 5.0.0 (July 27th, 2026): Compatible with Django 5.0
* FileBrowser 4.0.3 (July 27th, 2023): Compatible with Django 4.0

Current development branches:

* FileBrowser 5.0.1 (Development Version for Django 5.x, see Branch Stable/5.0.x)
* FileBrowser 4.0.4 (Development Version for Django 4.0, see Branch Stable/4.0.x)

Older versions are available at GitHub, but are not supported anymore.
