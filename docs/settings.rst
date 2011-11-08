:tocdepth: 2

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _settings:

Settings
========

There's quite a few possibilities of customizing the |filebrowser| to fit your needs. Nonetheless, you should be able to start with the default settings.

.. note::
    All settings can be defined in your projects settings-file or the FileBrowsers settings-file (``settings.py``). When using the projects settings-file, you have to use the prefix ``FILEBROWSER_`` for every setting (e.g. ``FILEBROWSER_MEDIA_URL`` instead of ``MEDIA_URL``). 

Main URL/Paths Settings
-----------------------

MEDIA_ROOT
^^^^^^^^^^

The absolute path to the directory that holds the media-files you want to browse::

    MEDIA_ROOT = getattr(settings, "FILEBROWSER_MEDIA_ROOT", settings.MEDIA_ROOT)

MEDIA_URL
^^^^^^^^^

URL that handles the media served from ``MEDIA_ROOT``::

    MEDIA_URL = getattr(settings, "FILEBROWSER_MEDIA_URL", settings.MEDIA_URL)

DIRECTORY (relative to ``MEDIA_ROOT``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Main FileBrowser Directory. Leave empty in order to browse all files and folders within MEDIA_ROOT::

    DIRECTORY = getattr(settings, "FILEBROWSER_DIRECTORY", 'uploads/')

FileBrowser Media, TinyMCE Media
--------------------------------

URL_FILEBROWSER_MEDIA, PATH_FILEBROWSER_MEDIA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The URL and Path to your FileBrowser media-files::

    URL_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_URL_FILEBROWSER_MEDIA", settings.STATIC_URL + "filebrowser/")
    PATH_FILEBROWSER_MEDIA = getattr(settings, "FILEBROWSER_PATH_FILEBROWSER_MEDIA", os.path.join(settings.STATIC_ROOT, 'filebrowser/'))

URL_TINYMCE, PATH_TINYMCE
^^^^^^^^^^^^^^^^^^^^^^^^^

The URL to your TinyMCE Installation::

    URL_TINYMCE = getattr(settings, "FILEBROWSER_URL_TINYMCE", settings.ADMIN_MEDIA_PREFIX + "tinymce/jscripts/tiny_mce/")
    PATH_TINYMCE = getattr(settings, "FILEBROWSER_PATH_TINYMCE", settings.ADMIN_MEDIA_PREFIX + "tinymce/jscripts/tiny_mce/")

.. note::
    Only change these settings if you're absolutely sure about what you're doing.

Extensions and Formats
----------------------

EXTENSIONS
^^^^^^^^^^

Allowed extensions for file upload::

    EXTENSIONS = getattr(settings, "FILEBROWSER_EXTENSIONS", {
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

Versions
--------

VERSIONS_BASEDIR (relative to ``MEDIA_ROOT``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionchanged:: 3.4.0

Directory to save image versions (and thumbnails). If no directory is given, versions are stored at the same location as the original image::

    VERSIONS_BASEDIR = getattr(settings, 'FILEBROWSER_VERSIONS_BASEDIR', '')

.. note::

    In versions previous to FileBrowser 3.4, it was possible to have VERSION_BASEDIR placed at a path which was not browsed by FileBrowser (by placing VERSION_BASEDIR anywhere else than under DIRECTORY). 

    However, this is not possible as of FileBrowser 3.4 because DIRECTORY variable is not used anymore and FileBrowser browses anything under MEDIA_ROOT. If you don't want FileBrowser to browse/display the contents of VERSION_BASEDIR, make this directory *hidden*.

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

ADMIN_VERSIONS
^^^^^^^^^^^^^^

The versions you want to show with the admin-interface::

    ADMIN_VERSIONS = getattr(settings, 'FILEBROWSER_ADMIN_VERSIONS', ['thumbnail', 'small', 'medium', 'big', 'large'])

ADMIN_THUMBNAIL
^^^^^^^^^^^^^^^

The version being used as the admin-thumbnail::

    ADMIN_THUMBNAIL = getattr(settings, 'FILEBROWSER_ADMIN_THUMBNAIL', 'admin_thumbnail')

.. _settingsplaceholder:

PLACEHOLDER
^^^^^^^^^^^

Path to placeholder image (relative to MEDIA_ROOT)::

    PLACEHOLDER = getattr(settings, "FILEBROWSER_PLACEHOLDER", "")

SHOW_PLACEHOLDER
^^^^^^^^^^^^^^^^

Show Placeholder (instead of a Version) if the original image does not exist::

    SHOW_PLACEHOLDER = getattr(settings, "FILEBROWSER_SHOW_PLACEHOLDER", False)

FORCE_PLACEHOLDER
^^^^^^^^^^^^^^^^^

Always show placeholder (even if the original image exists)::

    FORCE_PLACEHOLDER = getattr(settings, "FILEBROWSER_FORCE_PLACEHOLDER", False)

Extra Settings
--------------

SAVE_FULL_URL
^^^^^^^^^^^^^

.. deprecated:: 3.4.0
    With custom storage engines, saving the full URL (including MEDIA_ROOT) doesn´t make sense anymore. Moreover, removing this settings allows for easily replacing a FileBrowseField with Djangos File- or ImageField.

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

Options are: ``date``, ``filesize``, ``filename_lower``, ``filetype_checked``

DEFAULT_SORTING_ORDER
^^^^^^^^^^^^^^^^^^^^^

Default sorting order::

    DEFAULT_SORTING_ORDER = getattr(settings, "FILEBROWSER_DEFAULT_SORTING_ORDER", "desc")

Options are: ``asc`` or ``desc``

SEARCH_TRAVERSE
^^^^^^^^^^^^^^^

.. versionadded:: 3.3

``True``, if you want to traverse all subdirectories when searching. Please note that with thousands of files/directories, this might take a while::

    SEARCH_TRAVERSE = getattr(settings, "FILEBROWSER_SEARCH_TRAVERSE", False)

DEFAULT_PERMISSIONS
^^^^^^^^^^^^^^^^^^^

.. versionadded:: 3.3

Default Upload and Version Permissions::

    DEFAULT_PERMISSIONS = getattr(settings, "FILEBROWSER_DEFAULT_PERMISSIONS", 0755)
