# coding: utf-8

import os
import sys

from django.conf import settings
from django.core.management import call_command
from django.utils.six import StringIO

from filebrowser.settings import DIRECTORY
from tests import FilebrowserTestCase as TestCase


class VersionGenerateCommandTests(TestCase):

    def setUp(self):
        self.version_file = os.path.join(settings.MEDIA_ROOT, "_test/_versions/subfolder/testimage_large.jpg")

    def test_fb_version_generate(self):
        self.assertFalse(os.path.exists(self.version_file))

        sys.stdin = StringIO("large")
        call_command('fb_version_generate', DIRECTORY)

        self.assertTrue(os.path.exists(self.version_file))
