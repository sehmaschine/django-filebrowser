:tocdepth: 2

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _filelisting:

``FileListing`` class
=====================

The ``FileListing`` is a group of ``FileObjects`` for a given directory::

    filelisting = FileListing(path, filter_func=None, sorting_by=None, sorting_order=None)

For example, if you want to list all files for ``MEDIA_ROOT`` you can write::

    from filebrowser.settings import MEDIA_ROOT
    
    filelisting = FileListing(MEDIA_ROOT, sorting_by='date', sorting_order='desc')

Options
-------

``filter_func``
^^^^^^^^^^^^^^^

Filter function, based on a ``FileObject``::

    def filter_filelisting(item):
        return item.filetype != "Folder"

``sorting_by``
^^^^^^^^^^^^^^

Sort the files by any attribute of ``FileObject`` (e.g. ``filetype``, ``date``, ...).

``sorting_order``
^^^^^^^^^^^^^^^^^

Sorting order, either ``asc`` or ``desc``.

Attributes
----------

``listing``
^^^^^^^^^^^

Returns all items for the given path with ``os.listdir(path)``.

``walk``
^^^^^^^^

Returns all items for the given path with ``os.walk(path)``.

``files_listing_total``
^^^^^^^^^^^^^^^^^^^^^^^

Returns a sorted list of ``FileObjects`` for ``self.listing()``.

``files_walk_total``
^^^^^^^^^^^^^^^^^^^^

Returns a sorted list of ``FileObjects`` for ``self.walk()``.

``files_listing_filtered``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns a sorted and filtered list of ``FileObjects`` for ``self.listing()``.

``files_walk_filtered``
^^^^^^^^^^^^^^^^^^^^^^^

Returns a sorted and filtered list of ``FileObjects`` for ``self.walk()``.

``results_listing_total``
^^^^^^^^^^^^^^^^^^^^^^^^^

Number of total files, based on ``files_listing_total``.

``results_walk_total``
^^^^^^^^^^^^^^^^^^^^^^

Number of total files, based on ``files_walk_total``.

``results_listing_filtered``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Number of filtered files, based on ``files_listing_filtered``.

``results_walk_filtered``
^^^^^^^^^^^^^^^^^^^^^^^^^

Number of filtered files, based on ``files_walk_filtered``.

.. _fileobject:

``FileObject`` class
====================

When browsing a directory on the server, you get a ``FileObject`` (see ``base.py``) for every file within that directory. Set ``DEBUG`` to True in order to see the ``FileObject`` values::

    fileobject = FileObject("/absolute/server/path/to/file.ext")
    fileobject = FileObject("relative/server/path/to/file.ext", relative=True)

General attributes
------------------

``filename``
^^^^^^^^^^^^

Name of the file (including the extension) or name of the folder.

``filetype``
^^^^^^^^^^^^

Type of the file, as defined with ``EXTENSIONS``. With a folder, the filetype is "Folder".

``mimetype``
^^^^^^^^^^^^

.. versionadded:: 3.2

XXX

``filesize``
^^^^^^^^^^^^

display with ``filesizeformat``

``extension``
^^^^^^^^^^^^^

File extension, including the dot. With a folder, the extensions is ``None``.

``date``
^^^^^^^^

getmtime

``datetime``
^^^^^^^^^^^^

datetime object

Path and URL attributes
-----------------------

``path``
^^^^^^^^

Absolute server path to the file/folder, including ``MEDIA_ROOT``.

``path_relative``
^^^^^^^^^^^^^^^^^

Server path to the file/folder, relative to ``MEDIA_ROOT``.

``url_full``
^^^^^^^^^^^^

.. deprecated:: 3.2

see :ref:`url` instead.

``url``
^^^^^^^

.. versionadded:: 3.2

URL for the file/folder, including ``MEDIA_URL``.

``url_relative``
^^^^^^^^^^^^^^^^

URL for the file/folder, relative to ``MEDIA_URL``

``url_save``
^^^^^^^^^^^^

URL for the file/folder, used for the ``FileBrowseField`` (either ``url`` or ``url_relative``).

Image attributes
----------------

``dimensions``
^^^^^^^^^^^^^^

Image dimensions as a tuple.

``width``
^^^^^^^^^

Image width in px.

``height``
^^^^^^^^^^

Image height in px.

``orientation``
^^^^^^^^^^^^^^^

Image orientation, either "landscape" or "portrait".

Folder attributes
-----------------

``directory``
^^^^^^^^^^^^^

XXX

``is_empty``
^^^^^^^^^^^^

``true``, if the directory is empty (and thus can be deleted)