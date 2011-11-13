# coding: utf-8

# imports
import os

# django imports
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from filebrowser.settings import *

# VERSIONS
# Directory to Save Image Versions (and Thumbnails). Relative to MEDIA_ROOT.
# If no directory is given, versions are stored within the Image directory.
# VERSION URL: VERSIONS_BASEDIR/original_path/originalfilename_versionsuffix.extension
VERSIONS_BASEDIR = getattr(settings, 'FILEBROWSER_VERSIONS_BASEDIR', '')
# Versions Format. Available Attributes: verbose_name, width, height, opts
VERSIONS = getattr(settings, "FILEBROWSER_VERSIONS", {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    'thumbnail': {'verbose_name': 'Thumbnail (1 col)', 'width': 60, 'height': 60, 'opts': 'crop'},
    'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
    'medium': {'verbose_name': 'Medium (4col )', 'width': 300, 'height': '', 'opts': ''},
    'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
    'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''},
})
# Quality of saved versions
VERSION_QUALITY = getattr(settings, 'FILEBROWSER_VERSION_QUALITY', 90)
# Versions available within the Admin-Interface.
ADMIN_VERSIONS = getattr(settings, 'FILEBROWSER_ADMIN_VERSIONS', ['thumbnail', 'small', 'medium', 'big', 'large'])
# Which Version should be used as Admin-thumbnail.
ADMIN_THUMBNAIL = getattr(settings, 'FILEBROWSER_ADMIN_THUMBNAIL', 'admin_thumbnail')

# PLACEHOLDER
# Path to placeholder image
PLACEHOLDER = getattr(settings, "FILEBROWSER_PLACEHOLDER", "")
# Show Placeholder if the original image does not exist
SHOW_PLACEHOLDER = getattr(settings, "FILEBROWSER_SHOW_PLACEHOLDER", False)
# Always show placeholder (even if the original image exists)
FORCE_PLACEHOLDER = getattr(settings, "FILEBROWSER_FORCE_PLACEHOLDER", False)

# PIL's Error "Suspension not allowed here" work around:
# s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
IMAGE_MAXBLOCK = getattr(settings, 'FILEBROWSER_IMAGE_MAXBLOCK', 1024*1024)
# Exclude files matching any of the following regular expressions
# Default is to exclude 'thumbnail' style naming of image-thumbnails.
EXTENSION_LIST = []
for exts in EXTENSIONS.values():
    EXTENSION_LIST += exts
EXCLUDE = getattr(settings, 'FILEBROWSER_EXCLUDE', (r'_(%(exts)s)_.*_q\d{1,3}\.(%(exts)s)' % {'exts': ('|'.join(EXTENSION_LIST))},))
