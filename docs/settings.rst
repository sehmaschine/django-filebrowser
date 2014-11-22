:tocdepth: 2

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _settings:

Settings
========

There are some settings in order to customize the |filebrowser|. Nonetheless, you should be able to start with the default settings.

All settings can be defined in your projects settings-file. In that case, you have to use the prefix ``FILEBROWSER_`` for every setting (e.g. ``FILEBROWSER_EXTENSIONS`` instead of ``EXTENSIONS``). 

.. _settingsurlspaths:

Main URL/Paths Settings
-----------------------

MEDIA_ROOT
^^^^^^^^^^

.. warning::

    Will be removed with version 3.6.0. Since 3.4, MEDIA_ROOT is defined with your storage engine.

The absolute path to the directory that holds the media-files you want to browse::

    MEDIA_ROOT = getattr(settings, "FILEBROWSER_MEDIA_ROOT", settings.MEDIA_ROOT)

MEDIA_URL
^^^^^^^^^

.. warning::

    Will be removed with version 3.6.0. Since 3.4, MEDIA_URL is defined with your storage engine.

URL that handles the media served from MEDIA_ROOT::

    MEDIA_URL = getattr(settings, "FILEBROWSER_MEDIA_URL", settings.MEDIA_URL)

DIRECTORY (relative to storage location)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Main FileBrowser Directory. Leave empty in order to browse all files and folders within a storage location::

    DIRECTORY = getattr(settings, "FILEBROWSER_DIRECTORY", 'uploads/')

You can override this setting on a per–site basis::

    from filebrowser.sites import site
    site.directory = "uploads/"

FileBrowser Media, TinyMCE Media
--------------------------------

.. deprecated:: 3.5.3
    Use ``staticfiles`` instead.

.. _settingsextensionsformats:

Extensions and Formats
----------------------

EXTENSIONS
^^^^^^^^^^

Allowed extensions for file upload::

    EXTENSIONS = getattr(settings, "FILEBROWSER_EXTENSIONS", {
        'Folder': [''],
        'Image': ['.jpg','.jpeg','.gif','.png','.tif','.tiff'],
        'Document': ['.pdf','.doc','.rtf','.txt','.xls','.csv'],
        'Video': ['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
        'Audio': ['.mp3','.mp4','.wav','.aiff','.midi','.m4p']
    })

SELECT_FORMATS
^^^^^^^^^^^^^^

Set different Options for selecting elements from the FileBrowser::

    SELECT_FORMATS = getattr(settings, "FILEBROWSER_SELECT_FORMATS", {
        'file': ['Folder','Image','Document','Video','Audio'],
        'image': ['Image'],
        'document': ['Document'],
        'media': ['Video','Audio'],
    })

When using the browse-function for selecting Files/Folders, you can use an additional query-attribute ``type`` in order to restrict the choices.

.. _settingsversions:

Versions
--------

VERSIONS_BASEDIR (relative to storage location)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionchanged:: 3.4.0

Directory to save image versions (and thumbnails). If no directory is given, versions are stored at the same location as the original image::

    VERSIONS_BASEDIR = getattr(settings, 'FILEBROWSER_VERSIONS_BASEDIR', '')

We do recommend the following structure for media files::

    └── media  # site.storage.location (e.g. MEDIA_ROOT)
        ├── _versions  # VERSIONS_BASEDIR (outside of site.directory)
        └── uploads  # site.directory

.. warning::
    If VERSIONS_BASEDIR is within site.directory it will be browsed.

.. warning::
    With the next major release (3.6.0), the default setting will be "_versions".

VERSIONS
^^^^^^^^

Define the versions according to your websites grid::

    VERSIONS = getattr(settings, "FILEBROWSER_VERSIONS", {
        'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
        'thumbnail': {'verbose_name': 'Thumbnail (1 col)', 'width': 60, 'height': 60, 'opts': 'crop'},
        'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
        'medium': {'verbose_name': 'Medium (4col )', 'width': 300, 'height': '', 'opts': ''},
        'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
        'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''},
    })

VERSION_QUALITY
^^^^^^^^^^^^^^^

Quality of saved versions::

    VERSION_QUALITY = getattr(settings, 'FILEBROWSER_VERSION_QUALITY', 90)

ADMIN_VERSIONS
^^^^^^^^^^^^^^

The versions you want to show with the admin interface::

    ADMIN_VERSIONS = getattr(settings, 'FILEBROWSER_ADMIN_VERSIONS', ['thumbnail', 'small', 'medium', 'big', 'large'])

ADMIN_THUMBNAIL
^^^^^^^^^^^^^^^

The version being used as the admin thumbnail::

    ADMIN_THUMBNAIL = getattr(settings, 'FILEBROWSER_ADMIN_THUMBNAIL', 'admin_thumbnail')

.. _settingsplaceholder:

Placeholder
-----------

With your locale environment, you don't necessarily have access to all media files (e.g. images uploaded by your client). Therefore, you can use a PLACEHOLDER.

PLACEHOLDER
^^^^^^^^^^^

Path to placeholder image (relative to storage location)::

    PLACEHOLDER = getattr(settings, "FILEBROWSER_PLACEHOLDER", "")

SHOW_PLACEHOLDER
^^^^^^^^^^^^^^^^

Show placeholder (instead of a version) if the original image does not exist::

    SHOW_PLACEHOLDER = getattr(settings, "FILEBROWSER_SHOW_PLACEHOLDER", False)

FORCE_PLACEHOLDER
^^^^^^^^^^^^^^^^^

Always show placeholder (even if the original image exists)::

    FORCE_PLACEHOLDER = getattr(settings, "FILEBROWSER_FORCE_PLACEHOLDER", False)

.. _settingsextrasettings:

Extra Settings
--------------

SAVE_FULL_URL
^^^^^^^^^^^^^

.. deprecated:: 3.4.0
    With custom storage engines, saving the full URL doesn't make sense anymore. Moreover, removing this settings allows for easily replacing a FileBrowseField with Djangos File- or ImageField.

STRICT_PIL
^^^^^^^^^^

If set to ``True``, the FileBrowser will not try to import a mis-installed PIL::

    STRICT_PIL = getattr(settings, 'FILEBROWSER_STRICT_PIL', False)

IMAGE_MAXBLOCK
^^^^^^^^^^^^^^

see http://mail.python.org/pipermail/image-sig/1999-August/000816.html::

    IMAGE_MAXBLOCK = getattr(settings, 'FILEBROWSER_IMAGE_MAXBLOCK', 1024*1024)

EXCLUDE
^^^^^^^

Exclude-patterns for files you don't want to show::

    EXTENSION_LIST = []
    for exts in EXTENSIONS.values():
        EXTENSION_LIST += exts
    EXCLUDE = getattr(settings, 'FILEBROWSER_EXCLUDE', (r'_(%(exts)s)_.*_q\d{1,3}\.(%(exts)s)' % {'exts': ('|'.join(EXTENSION_LIST))},))

MAX_UPLOAD_SIZE
^^^^^^^^^^^^^^^

Max. Upload Size in Bytes::

    MAX_UPLOAD_SIZE = getattr(settings, "FILEBROWSER_MAX_UPLOAD_SIZE", 10485760)

NORMALIZE_FILENAME
^^^^^^^^^^^^^^^^^^

``True`` if you want to normalize filename on upload and remove all non-alphanumeric characters (except for underscores, spaces & dashes)::

    NORMALIZE_FILENAME = getattr(settings, "FILEBROWSER_NORMALIZE_FILENAME", False)

CONVERT_FILENAME
^^^^^^^^^^^^^^^^^

``True`` if you want to convert the filename on upload (replace spaces and convert to lowercase)::

    CONVERT_FILENAME = getattr(settings, "FILEBROWSER_CONVERT_FILENAME", True)

LIST_PER_PAGE
^^^^^^^^^^^^^

How many items appear on each paginated list::

    LIST_PER_PAGE = getattr(settings, "FILEBROWSER_LIST_PER_PAGE", 50)

DEFAULT_SORTING_BY
^^^^^^^^^^^^^^^^^^

Default sorting attribute::

    DEFAULT_SORTING_BY = getattr(settings, "FILEBROWSER_DEFAULT_SORTING_BY", "date")

Options are: ``date``, ``filesize``, ``filename_lower``, ``filetype_checked``, ``mimetype``

You can also use a few of them in one time eg. ``(mimetype, filename_lower)``

DEFAULT_SORTING_ORDER
^^^^^^^^^^^^^^^^^^^^^

Default sorting order::

    DEFAULT_SORTING_ORDER = getattr(settings, "FILEBROWSER_DEFAULT_SORTING_ORDER", "desc")

Options are: ``asc`` or ``desc``

FOLDER_REGEX
^^^^^^^^^^^^

regex to clean directory names before creation::

    FOLDER_REGEX = getattr(settings, "FILEBROWSER_FOLDER_REGEX", r'^[\w._\ /-]+$')

SEARCH_TRAVERSE
^^^^^^^^^^^^^^^

``True`` if you want to traverse all subdirectories when searching. Please note that with thousands of files/directories, this might take a while::

    SEARCH_TRAVERSE = getattr(settings, "FILEBROWSER_SEARCH_TRAVERSE", False)

DEFAULT_PERMISSIONS
^^^^^^^^^^^^^^^^^^^

Default upload and version permissions::

    DEFAULT_PERMISSIONS = getattr(settings, "FILEBROWSER_DEFAULT_PERMISSIONS", 0755)


OVERWRITE_EXISTING
^^^^^^^^^^^^^^^^^^

.. versionadded:: 3.5.1

``True`` in order to overwrite existing files. ``False`` to use the behaviour of the storage engine::

    OVERWRITE_EXISTING = getattr(settings, "FILEBROWSER_OVERWRITE_EXISTING", True)
