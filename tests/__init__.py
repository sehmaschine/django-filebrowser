import os
import shutil

from django.conf import settings
from django.test import TestCase

from filebrowser.settings import DIRECTORY
from filebrowser.base import FileObject
from filebrowser.sites import site


class FilebrowserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(FilebrowserTestCase, cls).setUpClass()
        cls.DIRECTORY_PATH = os.path.join(site.storage.location, DIRECTORY)
        cls.VERSION_PATH = os.path.join(site.storage.location, '_versions')

        cls.TEST_PATH = os.path.join(cls.DIRECTORY_PATH, 'filebrowser_test')
        cls.PLACEHOLDER_PATH = os.path.join(cls.DIRECTORY_PATH, 'placeholder_test')

        cls.STATIC_IMG_PATH = os.path.join(settings.BASE_DIR, 'filebrowser', "static", "filebrowser", "img", "testimage.jpg")
        cls.F_IMG = FileObject(os.path.join(DIRECTORY, 'filebrowser_test', "testimage.jpg"), site=site)
        cls.F_MISSING = FileObject(os.path.join(DIRECTORY, 'filebrowser_test', "missing.jpg"), site=site)

        os.makedirs(cls.TEST_PATH)
        os.makedirs(cls.PLACEHOLDER_PATH)
        shutil.copy(cls.STATIC_IMG_PATH, cls.TEST_PATH)
        shutil.copy(cls.STATIC_IMG_PATH, cls.PLACEHOLDER_PATH)

    @classmethod
    def tearDownClass(cls):
        super(FilebrowserTestCase, cls).tearDownClass()
        shutil.rmtree(cls.TEST_PATH)
        shutil.rmtree(cls.PLACEHOLDER_PATH)
        shutil.rmtree(cls.VERSION_PATH)
