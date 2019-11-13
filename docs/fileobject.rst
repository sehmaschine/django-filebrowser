:tocdepth: 3

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _fileobject:

FileObject
==========

.. class:: FileObject(path, site=None)

    An object representing a media file.

    :param path: Relative path to a location within `site.storage.location`.
    :param site: An optional FileBrowser Site.

For example:

.. code-block:: python

    from filebrowser.sites import site
    from filebrowser.base import FileObject
    fileobject = FileObject(os.path.join(site.directory,"testfolder","testimage.jpg"))
    version = FileObject(os.path.join(fileobject.versions_basedir, "testfolder", "testimage_medium.jpg"))

Attributes
----------

Initial Attributes
^^^^^^^^^^^^^^^^^^

.. attribute:: path

    Path relative to a storage location (including ``site.directory``)::

        >>> fileobject.path
        'uploads/testfolder/testimage.jpg'

.. attribute:: head

    The directory name of pathname ``path``::

        >>> fileobject.head
        'uploads/testfolder'

.. attribute:: filename

    Name of the file (including the extension) or name of the folder::

        >>> fileobject.filename
        'testimage.jpg'

.. attribute:: filename_lower

    Lower type of ``filename``.

.. attribute:: filename_root

    Filename without extension::

        >>> fileobject.filename_root
        'testimage'

.. attribute:: extension

    File extension, including the dot. With a folder, the extensions is ``None``::

        >>> fileobject.extension
        '.jpg'

.. attribute:: mimetype

    Mimetype, based on http://docs.python.org/library/mimetypes.html::

        >>> fileobject.mimetype
        ('image/jpeg', None)

General Attributes
^^^^^^^^^^^^^^^^^^

.. attribute:: filetype

    Type of the file, as defined with ``EXTENSIONS``::

        >>> fileobject.filetype
        'Image'

.. attribute:: format

    Type of the file, as defined with ``SELECT_FORMATS``::

        >>> fileobject.format
        'file'

.. attribute:: filesize

    Filesize in Bytes::

        >>> fileobject.filesize
        870037L

.. attribute:: date

    Date, based on ``time.mktime``::

        >>> fileobject.date
        1299760347.0

.. attribute:: datetime

    Datetime object::

        >>> fileobject.datetime
        datetime.datetime(2011, 3, 10, 13, 32, 27)

.. attribute:: exists

    ``True``, if the path exists, ``False`` otherwise::

        >>> fileobject.exists
        True

Path and URL attributes
^^^^^^^^^^^^^^^^^^^^^^^

.. attribute:: path

    Path relative to a storage location (including ``site.directory``)::

        >>> fileobject.path
        'uploads/testfolder/testimage.jpg'

.. attribute:: path_relative_directory

    Path relative to ``site.directory``::

        >>> fileobject.path_relative_directory
        'testfolder/testimage.jpg'

.. attribute:: path_full

    Absolute server path (based on ``storage.path``)::

        >>> fileobject.path_full
        '/absolute/path/to/server/location/testfolder/testimage.jpg'

.. attribute:: dirname

    .. versionadded:: 3.4

    The directory (not including ``site.directory``)::

        >>> fileobject.dirname
        'testfolder'

.. attribute:: url

    URL for the file/folder (based on ``storage.url``)::

        >>> fileobject.url
        '/media/uploads/testfolder/testimage.jpg'

Image attributes
^^^^^^^^^^^^^^^^

The image attributes are only useful if the ``FileObject`` represents an image.

.. attribute:: dimensions

    Image dimensions as a tuple::

        >>> fileobject.dimensions
        (1000, 750)

.. attribute:: width

    Image width in px::

        >>> fileobject.width
        1000

.. attribute:: height

    Image height in px::

        >>> fileobject.height
        750

.. attribute:: aspectratio

    Aspect ratio (float format)::

        >>> fileobject.aspectratio
        1.33534908

.. attribute:: orientation

    Image orientation, either ``Landscape`` or ``Portrait``::

        >>> fileobject.orientation
        'Landscape'

Folder attributes
^^^^^^^^^^^^^^^^^

The folder attributes make sense when the ``FileObject`` represents a directory (not a file).

.. attribute:: is_folder

    ``True``, if path is a folder::

        >>> fileobject.is_folder
        False

.. attribute:: is_empty

    ``True``, if the folder is empty. ``False`` if the folder is not empty or the ``FileObject`` is not a folder::

        >>> fileobject.is_empty
        False

Version attributes
^^^^^^^^^^^^^^^^^^

.. attribute:: is_version

    ``true`` if the File is a ``version`` of another File::

        >>> fileobject.is_version
        False
        >>> version.is_version
        True

.. attribute:: versions_basedir

    The relative path (from storage location) to the main versions folder. Either ``VERSIONS_BASEDIR`` or ``site.directory``::

        >>> fileobject.versions_basedir
        '_versions'
        >>> version.versions_basedir
        '_versions'

.. attribute:: original

    Returns the original FileObject::

        >>> fileobject.original
        <FileObject: uploads/testfolder/testimage.jpg>
        >>> version.original
        <FileObject: uploads/testfolder/testimage.jpg>

.. attribute:: original_filename

    Get the filename of an original image from a version::

        >>> fileobject.original_filename
        'testimage.jpg'
        >>> version.original_filename
        'testimage.jpg'

Methods
-------

Version methods
^^^^^^^^^^^^^^^

.. method:: versions()

    List all filenames based on ``VERSIONS``::

        >>> fileobject.versions()
        ['_versions/testfolder/testimage_admin_thumbnail.jpg',
        '_versions/testfolder/testimage_thumbnail.jpg',
        '_versions/testfolder/testimage_small.jpg',
        '_versions/testfolder/testimage_medium.jpg',
        '_versions/testfolder/testimage_big.jpg',
        '_versions/testfolder/testimage_large.jpg']
        >>> version.versions()
        []

    .. note::
        The versions are not being generated.

.. method:: admin_versions()

    List all filenames based on ``ADMIN_VERSIONS``::

        >>> fileobject.admin_versions()
        ['_versions/testfolder/testimage_thumbnail.jpg',
        '_versions/testfolder/testimage_small.jpg',
        '_versions/testfolder/testimage_medium.jpg',
        '_versions/testfolder/testimage_big.jpg',
        '_versions/testfolder/testimage_large.jpg']
        >>> version.admin_versions()
        []

    .. note::
        The versions are not being generated.

.. method:: version_name(version_suffix, extra_options=None)

    :param version_suffix: A suffix to compose the version name accordingly to
        the :ref:`settingsversions_version_namer` in use.
    :param extra_options: An optional ``dict`` to be used in the version generation.

    Get the filename for a version::

        >>> fileobject.version_name("medium")
        'testimage_medium.jpg'

    .. note::
        The version is not being generated.

    .. seealso::
        Files names can be customized using :ref:`settingsversions_version_namer`.

.. method:: version_path(version_suffix, extra_options=None)

    :param version_suffix: A suffix to compose the version name accordingly to
        the :ref:`settingsversions_version_namer` in use.
    :param extra_options: An optional ``dict`` to be used in the version generation.

    Get the path for a version::

        >>> fileobject.version_path("medium")
        '_versions/testfolder/testimage_medium.jpg'

    .. note::
        The version is not being generated.

.. _method_version_generate:

.. method:: version_generate(version_suffix, extra_options=None)

    :param version_suffix: A suffix to compose the version name accordingly to
        the :ref:`settingsversions_version_namer` in use.
    :param extra_options: An optional ``dict`` to be used in the version generation.

    An image version is generated by passing the source image through a series
    of :ref:`image processors <versions__custom_processors>`. Each processor
    may alter the image, often dependent on the options it receives.

    The options used in the processors chain is composed of the :ref:`version
    definition <versions>`, if ``version_suffix`` is a key in
    :ref:`settingsversions_versions`, plus any ``extra_options`` provided. If
    no version definition was found and no extra options are provided, an empty
    dict will be used. A key in ``extra_options`` will take precedence over the
    version definition.

    Generate a version::

        >>> fileobject.version_generate("medium")
        <FileObject: uploads/testfolder/testimage_medium.jpg>

    Please note that a version is only generated, if it does not already exist or if the original image is newer than the existing version.


Delete methods
^^^^^^^^^^^^^^

.. method:: delete()

    Delete the ``File`` or ``Folder`` from the server.

    .. warning::
        If you delete a **Folder**, all items within the folder are being deleted.

.. method:: delete_versions()

    Delete all ``VERSIONS``.

.. method:: delete_admin_versions()

    Delete all ``ADMIN_VERSIONS``.
