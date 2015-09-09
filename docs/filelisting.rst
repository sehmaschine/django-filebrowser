:tocdepth: 3

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _filelisting:

FileListing
===========

.. class:: FileListing(path, filter_func=None, sorting_by=None, sorting_order=None)

    Returns a list of FileObjects for a server path, see :ref:`fileobject`.

    :param path: Relative path to a location within `site.storage.location`.
    :param filter_func: Filter function, see example below.
    :param sorting_by: Sort the files by any attribute of FileObject.
    :param sorting_order: Sorting order, either "asc" or "desc".

If you want to list all files within a storage location you do:

.. code-block:: python

    from filebrowser.sites import site
    from filebrowser.base import FileListing
    filelisting = FileListing(site.storage.location, sorting_by='date', sorting_order='desc')

Use a custom filter function to limit the list of files:

.. code-block:: python

    def filter_filelisting(item):
        # item is a FileObject
        return item.filetype != "Folder"

    filelisting = FileListing(site.storage.location, filter_func=filter_listing, sorting_by='date', sorting_order='desc')

Methods
-------

For the below examples, we're using this folder-structure.::

    /media/uploads/testfolder/testimage.jpg
    /media/uploads/blog/1/images/blogimage.jpg

.. note::
    We defined ``filter_browse`` as ``filter_func`` (see sites.py). And we did not define a ``VERSIONS_BASEDIR`` for this demonstration, though it is highly recommended to use one.

.. method:: listing()

    Returns all items for the given path with ``os.listdir(path)``::

        >>> for item in filelisting.listing():
        ...     print item
        blog
        testfolder

.. method:: walk()

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

.. method:: files_listing_total()

    Returns a sorted list of ``FileObjects`` for :meth:`listing()`::

        >>> for item in filelisting.files_listing_total():
        ...     print item
        uploads/blog/
        uploads/testfolder/

.. method:: files_walk_total()

    Returns a sorted list of ``FileObjects`` for :meth:`walk()`::

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

.. method:: files_listing_filtered()

    Returns a sorted and filtered list of ``FileObjects`` for :meth:`listing()`::

        >>> for item in filelisting.files_listing_filtered():
        ...     print item
        uploads/blog/
        uploads/testfolder/

.. method:: files_walk_filtered()

    Returns a sorted and filtered list of ``FileObjects`` for :meth:`walk()`::

        >>> for item in filelisting.files_walk_filtered():
        ...     print item
        uploads/blog/
        uploads/blog/1/
        uploads/blog/1/images/
        uploads/blog/1/images/blogimage.jpg
        uploads/testfolder/
        uploads/testfolder/testimage.jpg

.. note::
    The versions are not listed (compared with files_walk_total) because of filter_func.

.. method:: results_listing_total()

    Number of total files, based on :meth:`files_listing_total()`::

        >>> filelisting.results_listing_total()
        2

.. method:: results_walk_total()

    Number of total files, based on :meth:`files_walk_total()`::

        >>> filelisting.results_walk_total()
        10

.. method:: results_listing_filtered()

    Number of filtered files, based on :meth:`files_listing_filtered()`::

        >>> filelisting.results_listing_filtered()
        2

.. method:: results_walk_filtered()

    Number of filtered files, based on :meth:`files_walk_filtered()`::

        >>> filelisting.results_walk_filtered()
        6
