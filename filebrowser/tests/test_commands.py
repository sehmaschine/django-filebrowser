# coding: utf-8

# PYTHON IMPORTS
import os
import ntpath
import posixpath
import shutil
import sys

# DJANGO IMPORTS
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.encoding import filepath_to_uri
from django.template import Context, Template, TemplateSyntaxError
from django.core.management import call_command
from django.utils.six import StringIO

# FILEBROWSER IMPORTS
import filebrowser
from filebrowser.base import FileObject, FileListing
from filebrowser.templatetags.fb_versions import version, version_object, version_setting
from filebrowser.sites import site
from filebrowser.management.commands import fb_version_generate, fb_version_remove

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
FILEBROWSER_PATH = os.path.split(TESTS_PATH)[0]


class CommandsTests(TestCase):

    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_path = filebrowser.base.os.path
        self.original_directory = site.directory
        self.original_versions_basedir = filebrowser.base.VERSIONS_BASEDIR
        self.original_versions = filebrowser.base.VERSIONS
        self.original_admin_versions = filebrowser.base.ADMIN_VERSIONS
        self.stdin = sys.stdin

        # DIRECTORY
        # custom directory because this could be set with sites
        # and we cannot rely on filebrowser.settings
        self.directory = "fb_test_directory/"
        self.directory_path = os.path.join(site.storage.location, self.directory)
        if os.path.exists(self.directory_path):
            self.fail("Test directory already exists.")
        else:
            os.makedirs(self.directory_path)
        # set site directory
        site.directory = self.directory

        # VERSIONS
        self.versions = "_versionstestdirectory"
        self.versions_path = os.path.join(site.storage.location, self.versions)
        if os.path.exists(self.versions_path):
            self.fail("Versions directory already exists.")
        else:
            os.makedirs(self.versions_path)

        # create temporary test folder and move testimage
        self.tmpdir_name = os.path.join("fb_tmp_dir", "fb_tmp_dir_sub")
        self.tmpdir_path = os.path.join(site.storage.location, self.directory, self.tmpdir_name)
        if os.path.exists(self.tmpdir_path):
            self.fail("Temporary testfolder already exists.")
        else:
            os.makedirs(self.tmpdir_path)

        # copy test image to temporary test folder
        self.image_path = os.path.join(FILEBROWSER_PATH, "static", "filebrowser", "img", "testimage.jpg")
        if not os.path.exists(self.image_path):
            self.fail("Testimage not found.")
        shutil.copy(self.image_path, self.tmpdir_path)

        # set posixpath
        filebrowser.base.os.path = posixpath

        # fileobjects
        self.f_image = FileObject(os.path.join(self.directory, self.tmpdir_name, "testimage.jpg"), site=site)
        self.f_image_not_exists = FileObject(os.path.join(self.directory, self.tmpdir_name, "testimage_does_not_exist.jpg"), site=site)
        self.f_folder = FileObject(os.path.join(self.directory, self.tmpdir_name), site=site)

    def test_fb_version_generate(self):
        """
        Templatetag version
        """
        # new settings
        filebrowser.base.VERSIONS_BASEDIR = "fb_test_directory/_versions"
        filebrowser.base.VERSIONS = {
            'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
            'large': {'verbose_name': 'Large', 'width': 600, 'height': '', 'opts': ''},
        }
        filebrowser.base.ADMIN_VERSIONS = ['large']
        filebrowser.settings.VERSIONS = filebrowser.base.VERSIONS
        filebrowser.management.commands.fb_version_generate.VERSIONS = filebrowser.base.VERSIONS
        filebrowser.management.commands.fb_version_remove.VERSIONS = filebrowser.base.VERSIONS

        # no versions
        self.assertEqual(os.path.exists(os.path.join(settings.MEDIA_ROOT, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg")), False)

        sys.stdin = StringIO("large")
        call_command('fb_version_generate', 'fb_test_directory')

        # versions
        self.assertEqual(os.path.exists(os.path.join(settings.MEDIA_ROOT, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg")), True)

    def test_fb_version_remove(self):
        """
        Test management command fb_verison_remove
        """
        pass

    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory
        filebrowser.base.VERSIONS_BASEDIR = self.original_versions_basedir
        filebrowser.base.VERSIONS = self.original_versions
        filebrowser.settings.VERSIONS = self.original_versions
        filebrowser.management.commands.fb_version_generate.VERSIONS = self.original_versions
        filebrowser.management.commands.fb_version_remove.VERSIONS = self.original_versions
        filebrowser.base.ADMIN_VERSIONS = self.original_admin_versions
        sys.stdin = self.stdin

        # remove temporary directory and test folder
        shutil.rmtree(self.directory_path)
        shutil.rmtree(self.versions_path)
