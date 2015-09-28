import os
import shutil

from django.conf import settings
from django.test import TestCase

from filebrowser.settings import DIRECTORY, VERSIONS_BASEDIR
from filebrowser.base import FileObject
from filebrowser.sites import site


class FilebrowserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.DIRECTORY = DIRECTORY
        cls.TEST_PATH = os.path.join(site.storage.location, '_test')
        cls.DIRECTORY_PATH = os.path.join(site.storage.location, DIRECTORY)
        cls.VERSIONS_PATH = os.path.join(site.storage.location, VERSIONS_BASEDIR)

        cls.FOLDER_PATH = os.path.join(cls.DIRECTORY_PATH, 'folder')
        cls.SUBFOLDER_PATH = os.path.join(cls.FOLDER_PATH, 'subfolder')
        cls.PLACEHOLDER_PATH = os.path.join(cls.DIRECTORY_PATH, 'placeholders')

        cls.STATIC_IMG_PATH = os.path.join(settings.BASE_DIR, 'filebrowser', "static", "filebrowser", "img", "testimage.jpg")

        cls.F_IMAGE = FileObject(os.path.join(DIRECTORY, 'folder', "testimage.jpg"), site=site)
        cls.F_MISSING = FileObject(os.path.join(DIRECTORY, 'folder', "missing.jpg"), site=site)
        cls.F_FOLDER = FileObject(os.path.join(DIRECTORY, 'folder'), site=site)
        cls.F_SUBFOLDER = FileObject(os.path.join(DIRECTORY, 'folder', 'subfolder'), site=site)

        super(FilebrowserTestCase, cls).setUpClass()

    def setUp(self):
        os.makedirs(self.FOLDER_PATH)
        os.makedirs(self.SUBFOLDER_PATH)
        shutil.copy(self.STATIC_IMG_PATH, self.FOLDER_PATH)

    def tearDown(self):
        shutil.rmtree(self.TEST_PATH)
