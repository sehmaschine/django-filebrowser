.. Django FileBrowser documentation master file, created by
   sphinx-quickstart on Sun Dec  5 19:11:46 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

Django FileBrowser Documentation
================================

**Media-Management with Grappelli**.

This documentation covers version 3.5.2 of the |filebrowser|.

.. note::
    |filebrowser| |version| requires Django 1.4/1.5 and |grappelli| 2.4. |filebrowser| is always developed against the lastest stable Django release and is NOT tested with Djangos trunk.

**Installation and Setup**

.. toctree::
   :maxdepth: 3
   
   quickstart
   settings

**FileBrowser Sites**

.. toctree::
   :maxdepth: 2
   
   sites  
   actions
   file_storages

**FileBrowser API**

.. toctree::
  :maxdepth: 2

  api

**Admin Interface**

.. toctree::
   :maxdepth: 3
   
   admin

**Fields and Widgets**

.. toctree::
   :maxdepth: 3
   
   fieldswidgets

**Image Versions**

.. toctree::
   :maxdepth: 3
   
   versions

**Help**

.. toctree::
   :maxdepth: 2
   
   faq
   troubleshooting
   translation
   releasenotes
   changelog

Main Features
-------------

* Browse your media files with the admin-interface.
* Multiple Upload, including a progress bar.
* Automatic Thumbnails.
* Image-Versions to fit your websites grid (esp. useful with adaptive/responsive layouts).
* Integration with TinyMCE (AdvImage & AdvLink).
* ``FileBrowseField`` to select Images/Documents.
* ``FileInput`` and ``ClearableFileInput`` with Image-Preview.
* Signals for Upload, Rename and Delete.
* Custom Actions.
* Custom File Storage Engines.

Code
----

https://github.com/sehmaschine/django-filebrowser

Discussion
----------

Use the `FileBrowser Google Group <http://groups.google.com/group/django-filebrowser>`_ to ask questions or discuss features.

Versions and Compatibility
--------------------------

* |filebrowser| 3.5.x: Requires |grappelli| 2.4 and Django 1.4 (3.5.1 is also compatible with Django 1.5)
* |filebrowser| 3.4.x: Requires |grappelli| 2.3 and Django 1.3

Older versions are availabe at GitHub, but are not supported anymore.


