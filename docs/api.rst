:tocdepth: 2

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _filelisting:

``FileListing`` class
=====================

The ``FileListing`` is a group of ``FileObjects`` for a given directory::

    filelisting = FileListing(path, filter_func=None, sorting_by=None, sorting_order=None)

For example, if you want to list all files within a storage location you can type::

    from filebrowser.sites import site
    from filebrowser.base import FileListing
    filelisting = FileListing(site.storage.location, sorting_by='date', sorting_order='desc')

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

For the below examples, we're using this folder-structure and ``filter_browse`` as ``filter_func`` (see ``views.py``)::

    /media/uploads/testfolder/testimage.jpg
    /media/uploads/blog/1/images/blogimage.jpg

``listing``
^^^^^^^^^^^

Returns all items for the given path with ``os.listdir(path)``::

    >>> for item in filelisting.listing():
    ...     print item
    blog
    testfolder

``walk``
^^^^^^^^

Returns all items for the given path with ``os.walk(path)``::

    >>> for item in filelisting.walk():
    ...     print item
    blog
    blog/1
    blog/1/images
    blog/1/images/blogimage.jpg
    blog/1/images/blogimage_admin_thumbnail.jpg
    blog/1/images/blogimage_medium.jpg
    blog/1/images/blogimage_small.jpg
    blog/1/images/blogimage_thumbnail.jpg
    testfolder
    testfolder/testimage.jpg

``files_listing_total``
^^^^^^^^^^^^^^^^^^^^^^^

Returns a sorted list of ``FileObjects`` for ``self.listing()``::

    >>> for item in filelisting.walk():
    ...     print item
    uploads/blog/
    uploads/testfolder/

``files_walk_total``
^^^^^^^^^^^^^^^^^^^^

Returns a sorted list of ``FileObjects`` for ``self.walk()``::

    >>> for item in filelisting.files_walk_total():
    ...     print item
    uploads/blog/
    uploads/blog/1/
    uploads/blog/1/images/
    uploads/blog/1/images/blogimage.jpg
    uploads/blog/1/images/blogimage_admin_thumbnail.jpg
    uploads/blog/1/images/blogimage_medium.jpg
    uploads/blog/1/images/blogimage_small.jpg
    uploads/blog/1/images/blogimage_thumbnail.jpg
    uploads/testfolder/
    uploads/testfolder/testimage.jpg

``files_listing_filtered``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns a sorted and filtered list of ``FileObjects`` for ``self.listing()``::

    >>> for item in filelisting.files_listing_filtered():
    ...     print item
    uploads/blog/
    uploads/testfolder/

``files_walk_filtered``
^^^^^^^^^^^^^^^^^^^^^^^

Returns a sorted and filtered list of ``FileObjects`` for ``self.walk()``::

    >>> for item in filelisting.files_walk_filtered():
    ...     print item
    uploads/blog/
    uploads/blog/1/
    uploads/blog/1/images/
    uploads/blog/1/images/blogimage.jpg
    uploads/testfolder/
    uploads/testfolder/testimage.jpg

.. note::
    The versions are not listed (compared with files_walk_total) because of ``filter_func``.

``results_listing_total``
^^^^^^^^^^^^^^^^^^^^^^^^^

Number of total files, based on ``files_listing_total``::

    >>> filelisting.results_listing_total()
    2

``results_walk_total``
^^^^^^^^^^^^^^^^^^^^^^

Number of total files, based on ``files_walk_total``::

    >>> filelisting.results_listing_total()
    10

``results_listing_filtered``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Number of filtered files, based on ``files_listing_filtered``::

    >>> filelisting.results_listing_filtered()
    2

``results_walk_filtered``
^^^^^^^^^^^^^^^^^^^^^^^^^

Number of filtered files, based on ``files_walk_filtered``::

    >>> filelisting.results_walk_filtered()
    6

.. _fileobject:

``FileObject`` class
====================

When browsing a directory on the server, you get a ``FileObject`` for every file within that directory. The ``FileObject`` is also returned when using the ``FileBrowseField``::

    fileobject = FileObject("relative/server/path/to/storage/location/file.ext")

For the examples below we use::

    from filebrowser.sites import site
    from filebrowser.base import FileObject
    fileobject = FileObject(os.path.join(site.directory,"testfolder","testimage.jpg"))

General attributes
------------------

``filename``
^^^^^^^^^^^^

Name of the file (including the extension) or name of the folder::

    >>> fileobject.filename
    'testimage.jpg'

``filetype``
^^^^^^^^^^^^

Type of the file, as defined with ``EXTENSIONS``::

    >>> fileobject.filetype
    'Image'

``mimetype``
^^^^^^^^^^^^

.. versionadded:: 3.3

Mimetype, based on http://docs.python.org/library/mimetypes.html::

    >>> fileobject.mimetype
    ('image/jpeg', None)

``filesize``
^^^^^^^^^^^^

Filesize in Bytes::

    >>> fileobject.filesize
    870037L

``extension``
^^^^^^^^^^^^^

File extension, including the dot. With a folder, the extensions is ``None``::

    >>> fileobject.extension
    '.jpg'

``date``
^^^^^^^^

Date, based on ``time.mktime``::

    >>> fileobject.date
    1299760347.0

``datetime``
^^^^^^^^^^^^

Datetime object::

    >>> fileobject.datetime
    datetime.datetime(2011, 3, 10, 13, 32, 27)

``exists``
^^^^^^^^^^^^

``True``, if the path exists, ``False`` otherwise::

    >>> fileobject.exists
    True

Path and URL attributes
-----------------------

``path``
^^^^^^^^

Path relative to a storage location (including ``site.directory``)::

    >>> fileobject.path
    'uploads/testfolder/testimage.jpg'

``path_relative_directory``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Path relative to ``site.directory``::

    >>> fileobject.path_relative_directory
    u'testfolder/testimage.jpg'

``path_full``
^^^^^^^^^^^^^

Absolute server path (equals ``storage.path``)::

    >>> fileobject.path_full
    u'/absolute/path/to/server/location/testfolder/testimage.jpg'

``dirname``
^^^^^^^^^^^

.. versionadded:: 3.4

The directory (not including ``site.directory``)::

    >>> fileobject.dirname
    u'testfolder'

``url``
^^^^^^^

.. versionadded:: 3.3

URL for the file/folder (equals ``storage.url``)::

    >>> fileobject.url
    u'/media/uploads/testfolder/testimage.jpg'

``url_full``, ``url_relative``, ``url_save``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. deprecated:: 3.3
    Use ``url`` instead.

Image attributes
----------------

The image attributes are only useful if the ``FileObject`` represents an image.

``dimensions``
^^^^^^^^^^^^^^

Image dimensions as a tuple::

    >>> fileobject.dimensions
    (1000, 750)

``width``
^^^^^^^^^

Image width in px::

    >>> fileobject.width
    1000

``height``
^^^^^^^^^^

Image height in px::

    >>> fileobject.height
    750

``aspectratio``
^^^^^^^^^^^^^^^

Aspect ratio (float format)::

    >>> fileobject.aspectratio
    1.33534908

``orientation``
^^^^^^^^^^^^^^^

Image orientation, either ``Landscape`` or ``Portrait``::

    >>> fileobject.orientation
    'Landscape'

Folder attributes
-----------------

The folder attributes make sense when the ``FileObject`` represents a directory (not a file).

``directory``
^^^^^^^^^^^^^

Folder(s) relative from ``site.directory``::

    >>> fileobject.directory
    u'testfolder'

``folder``
^^^^^^^^^^

Parent folder(s)::

    >>> fileobject.folder
    u'testfolder'

``is_folder``
^^^^^^^^^^^^^

``True``, if path is a folder::

    >>> fileobject.is_folder
    False

``is_empty``
^^^^^^^^^^^^

``True``, if the folder is empty::

    >>> fileobject.is_empty
    False

Version attributes
------------------

``is_version``
^^^^^^^^^^^^^^

``true`` if the File is a ``version`` of another File::

    >>> fileobject.is_version
    False

``versions_basedir``
^^^^^^^^^^^^^^^^^^^

The relative path (from storage location) to the main versions folder. Either ``VERSIONS_BASEDIR`` or ``site.directory`::

    >>> fileobject.versions_basedir
    'uploads'

``version_name(version_suffix)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get the filename for a version::

    >>> fileobject.version_name("medium")
    'testimage_medium.jpg'

.. note::
    The version is not being generated.

``versions()``
^^^^^^^^^^^^^^

List all filenames based on ``VERSIONS``::

    >>> fileobject.versions()
    ['/var/www/testsite/media/uploads/testfolder/testimage_admin_thumbnail.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_thumbnail.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_small.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_medium.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_big.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_large.jpg']

.. note::
    The versions are not being generated.

``admin_versions()``
^^^^^^^^^^^^^^^^^^^^

List all filenames based on ``ADMIN_VERSIONS``::

    >>> fileobject.admin_versions()
    ['/var/www/testsite/media/uploads/testfolder/testimage_thumbnail.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_small.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_medium.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_big.jpg',
    '/var/www/testsite/media/uploads/testfolder/testimage_large.jpg']

.. note::
    The versions are not being generated.

``version_generate(version_suffix)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generate a version::

    >>> fileobject.version_generate("medium")
    <FileObject: uploads/testfolder/testimage_medium.jpg>

Delete Functions
----------------

``delete()``
^^^^^^^^^^^^

Delete the ``File`` or ``Folder`` from the server.

.. warning::
    If you delete a ``Folder``, all items within the folder are being deleted. Be very careful with using this!

``delete_versions()``
^^^^^^^^^^^^^^^^^^^^^

Delete all ``VERSIONS``.

``delete_admin_versions()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Delete all ``ADMIN_VERSIONS``.