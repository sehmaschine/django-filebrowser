.. Django FileBrowser documentation master file, created by
   sphinx-quickstart on Sun Dec  5 19:11:46 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

Django FileBrowser Documentation
================================

**Media-Management with the Django admin-interface**.

This documentation covers version 3.3.0 of the |filebrowser|. With the |filebrowser|, you're able to browse your media-directory
and upload/rename/delete files and folders.

**Installation and Setup**

.. toctree::
   :maxdepth: 3
   
   quickstart
   settings

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

* Browse your media-directory with the admin-interface.
* Multiple Upload using `Uploadify <http://www.uploadify.com>`_.
* Automatic Thumbnails.
* Image-Versions to fit your websites grid.
* Integration with TinyMCE (AdvImage & AdvLink).
* ``FileBrowseField`` to select Images/Documents.
* ``ClearableFileInput`` with Image-Preview.
* Signals for Upload, Rename and Delete.

Code
----

http://code.google.com/p/django-filebrowser/

Discussion
----------

Use the `FileBrowser Google Group <http://groups.google.com/group/django-filebrowser>`_ to ask questions or discuss features.

