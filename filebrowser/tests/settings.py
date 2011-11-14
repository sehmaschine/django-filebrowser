# coding: utf-8

# PYTHON IMPORTS
import os

# DJANGO IMPORTS
from django.test import TestCase
from django.contrib.auth.models import User

# FILEBROWSER IMPORTS
from filebrowser.settings import *


class SettingsTests(TestCase):
    
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
