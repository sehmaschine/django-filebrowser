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
    |filebrowser| 3.5.8 requires Django 1.4/1.5/1.6 or 1.7 and |grappelli| 2.4/2.5 or 2.6.

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
   changelog

Main Features
-------------

* Browse your media files with the admin interface.
* Multiple upload, including a progress bar.
* Automatic thumbnails.
* Image versions to fit your websites grid (esp. useful with adaptive/responsive layouts).
* Integration with TinyMCE.
* FileBrowseField to select images/documents.
* FileInput and ClearableFileInput with image preview.
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

* FileBrowser 3.5.8 (Development Version, not yet released, see Branch Stable/3.5.x)
* FileBrowser 3.5.7 (September 10th, 2014): Compatible with Django 1.4/1.5/1.6/1.7

Older versions are available at GitHub, but are not supported anymore.