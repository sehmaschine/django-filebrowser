import os
import shutil

from django.conf import settings
from django.test import TestCase

from filebrowser.settings import DIRECTORY, VERSIONS_BASEDIR
from filebrowser.base import FileObject
from filebrowser.sites import site


class FilebrowserTestCase(TestCase):

    def setUp(self):
        self.DIRECTORY = DIRECTORY
        self.TEST_PATH = os.path.join(site.storage.location, '_test')
        self.DIRECTORY_PATH = os.path.join(site.storage.location, DIRECTORY)
        self.VERSIONS_PATH = os.path.join(site.storage.location, VERSIONS_BASEDIR)

        if os.path.exists(self.TEST_PATH):
            raise Exception('TEST_PATH Already Exists')

        self.FOLDER_PATH = os.path.join(self.DIRECTORY_PATH, 'folder')
        self.SUBFOLDER_PATH = os.path.join(self.FOLDER_PATH, 'subfolder')
        self.PLACEHOLDER_PATH = os.path.join(self.DIRECTORY_PATH, 'placeholders')

        self.STATIC_IMG_PATH = os.path.join(settings.BASE_DIR, 'filebrowser', "static", "filebrowser", "img", "testimage.jpg")

        self.F_IMAGE = FileObject(os.path.join(DIRECTORY, 'folder', "testimage.jpg"), site=site)
        self.F_MISSING = FileObject(os.path.join(DIRECTORY, 'folder', "missing.jpg"), site=site)
        self.F_FOLDER = FileObject(os.path.join(DIRECTORY, 'folder'), site=site)
        self.F_SUBFOLDER = FileObject(os.path.join(DIRECTORY, 'folder', 'subfolder'), site=site)

        os.makedirs(self.FOLDER_PATH)
        os.makedirs(self.SUBFOLDER_PATH)

    def tearDown(self):
        shutil.rmtree(self.TEST_PATH)
