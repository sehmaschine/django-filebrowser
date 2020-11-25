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
    |filebrowser| 3.13.2 requires Django 3.1 and |grappelli| 2.14.

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

* FileBrowser 3.13.2 (November 25th, 2020): Compatible with Django 3.1
* FileBrowser 3.12.1 (November 14th, 2019): Compatible with Django 2.2 (LTS)
* FileBrowser 3.9.2 (November 2nd, 2018): Compatible with Django 1.11 (LTS)

Current development branches:

* FileBrowser 3.13.3 (Development Version for Django 3.1, see Branch Stable/3.13.x)
* FileBrowser 3.12.2 (Development Version for Django 2.2, see Branch Stable/3.12.x)
* FileBrowser 3.9.3 (Development Version for Django 1.11, see Branch Stable/3.9.x)

Older versions are available at GitHub, but are not supported anymore.
Support for 3.12.x and 3.9.x is limited to security issues and very important bugfixes.
