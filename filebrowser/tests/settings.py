# coding: utf-8

# PYTHON IMPORTS
import os

# DJANGO IMPORTS
from django.test import TestCase
from django.contrib.auth.models import User

# FILEBROWSER IMPORTS
from filebrowser.settings import *


class SettingsTests(TestCase):
    
    def setUp(self):
        pass
    
    def test_media_root(self):
        """
        Test that ``MEDIA_ROOT`` exists.
        """
        self.assertEqual(os.path.exists(MEDIA_ROOT), 1)
    
    def test_directory(self):
        """
        Test that ``MEDIA_ROOT`` plus ``DIRECTORY`` exists.
        """
        self.assertEqual(os.path.exists(os.path.join(MEDIA_ROOT,DIRECTORY)), 1)
        # Check for trailing slash
        self.assertEqual(os.path.basename(DIRECTORY), '')
    
    def test_path_filebrowser_media(self):
        """
        Test that ``PATH_FILEBROWSER_MEDIA`` exists.
        """
        self.assertEqual(os.path.exists(PATH_FILEBROWSER_MEDIA), 1)
    
    def test_versions_basedir(self):
        """
        Test that ``MEDIA_ROOT`` plus ``VERSIONS_BASEDIR`` exists.
        """
        self.assertEqual(os.path.exists(os.path.join(MEDIA_ROOT,VERSIONS_BASEDIR)), 1)
    
    def test_admin_thumbnail(self):
        """
        Test if ``ADMIN_THUMBNAIL`` is set and is part of ``VERSIONS``.
        """
        self.assertNotEqual(ADMIN_THUMBNAIL, '')
        self.assertIn(ADMIN_THUMBNAIL, VERSIONS)
    
    def test_admin_versions(self):
        """
        Test if ``ADMIN_VERSIONS`` are part of ``VERSIONS``.
        """
        for item in ADMIN_VERSIONS:
            self.assertIn(item, VERSIONS)
    
    def test_strict_pil(self):
        """
        Test if ``STRICT_PIL`` is in ``True, False``.
        """
        self.assertIn(STRICT_PIL, [True, False])

    def test_normalize_filename(self):
        """
        Test if ``NORMALIZE_FILENAME`` is in ``True, False``.
        """
        self.assertIn(NORMALIZE_FILENAME, [True, False])

    def test_convert_filename(self):
        """
        Test if ``CONVERT_FILENAME`` is in ``True, False``.
        """
        self.assertIn(CONVERT_FILENAME, [True, False])
    
    def test_default_sorting_by(self):
        """
        Test if ``DEFAULT_SORTING_BY`` is in ``date, filesize, filename_lower, filetype_checked``.
        """
        self.assertIn(DEFAULT_SORTING_BY, ['date','filesize','filename_lower','filetype_checked'])
    
    def test_default_sorting_order(self):
        """
        Test if ``DEFAULT_SORTING_ORDER`` is in ``asc, desc``.
        """
        self.assertIn(DEFAULT_SORTING_ORDER, ['asc','desc'])
    
    def test_search_traverse(self):
        """
        Test if ``SEARCH_TRAVERSE`` is in ``True, False``.
        """
        self.assertIn(SEARCH_TRAVERSE, [True, False])


