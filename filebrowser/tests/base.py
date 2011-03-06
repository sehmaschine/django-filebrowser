# coding: utf-8

# PYTHON IMPORTS
import os

# DJANGO IMPORTS
from django.test import TestCase
from django.contrib.auth.models import User

# PYTHON IMPORTS
from filebrowser.settings import *


class BaseTests(TestCase):
    
    def setUp(self):
        """
        Copy sample Image to ``DIRECTORY``.
        Create folder.
        Copy sample Image to folder.
        """
    
    def test_filelisting(self):
        """
        Test if ``DEBUG`` is in ``True, False``.
        """
        self.assertIn(DEBUG, [True, False])
    
    def test_fileobject(self):
        """
        Test that ``MEDIA_ROOT`` exists.
        """
        self.assertEqual(os.path.exists(MEDIA_ROOT), 1)


