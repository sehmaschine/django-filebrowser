# coding: utf-8

"""
Tests for FileBrowser sites and their views.

Note that we *dynamically generate* test cases for each deployed FileBrowser
site. This includes creation of TestCase subclasses at runtime and also
creation of instance methods from functions.
"""

# PYTHON IMPORTS
from __future__ import with_statement
import os
import json
import shutil

from mock import patch

# DJANGO IMPORTS
from django.core.urlresolvers import reverse
from django.conf import settings
try:
    from django.utils.six.moves.urllib.parse import urlencode
except:
    from django.utils.http import urlencode

# FILEBROWSER IMPORTS
import filebrowser
from filebrowser.settings import VERSIONS, DEFAULT_PERMISSIONS
from filebrowser.base import FileObject
from filebrowser.sites import site
from tests import FilebrowserTestCase as TestCase

FILEBROWSER_PATH = os.path.join(settings.BASE_DIR, 'filebrowser')


class BrowseViewTests(TestCase):
    def setUp(self):
        super(BrowseViewTests, self).setUp()
        self.url = reverse('filebrowser:fb_browse')
        self.client.login(username=self.user.username, password='password')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertTrue(response.status_code == 200)
        self.assertTrue('filebrowser/index.html' in [t.name for t in response.templates])

        # Check directory was set correctly in the context. If this fails, it may indicate
        # that two sites were instantiated with the same name.
        self.assertTrue(site.directory == response.context['filebrowser_site'].directory)


class CreateDirViewTests(TestCase):
    def setUp(self):
        super(CreateDirViewTests, self).setUp()
        self.url = reverse('filebrowser:fb_createdir')
        self.client.login(username=self.user.username, password='password')

    def test_post(self):
        self.assertFalse(site.storage.exists(self.CREATEFOLDER_PATH))
        response = self.client.post(self.url, {'name': self.F_CREATEFOLDER.path_relative_directory})
        self.assertTrue(response.status_code == 302)
        self.assertTrue(site.storage.exists(self.CREATEFOLDER_PATH))


def test_ckeditor_params_in_search_form(test):
    """
    The CKEditor GET params must be included in the search form as hidden
    inputs so they persist after searching.
    """
    url = reverse('%s:fb_browse' % test.site_name)
    response = test.c.get(url, {
        'pop': '3',
        'type': 'image',
        'CKEditor': 'id_body',
        'CKEditorFuncNum': '1',
    })

    test.assertTrue(response.status_code == 200)
    test.assertContains(response, '<input type="hidden" name="pop" value="3" />')
    test.assertContains(response, '<input type="hidden" name="type" value="image" />')
    test.assertContains(response, '<input type="hidden" name="CKEditor" value="id_body" />')
    test.assertContains(response, '<input type="hidden" name="CKEditorFuncNum" value="1" />')


class UploadViewTests(TestCase):
    def setUp(self):
        super(UploadViewTests, self).setUp()
        self.url = reverse('filebrowser:fb_upload')
        self.client.login(username=self.user.username, password='password')

    def test_get(self):
        response = self.client.get(self.url, {'name': self.F_CREATEFOLDER.path_relative_directory})
        self.assertTrue(response.status_code == 200)
        self.assertTrue('filebrowser/upload.html' in [t.name for t in response.templates])


class UploadFileViewTests(TestCase):
    def setUp(self):
        super(UploadFileViewTests, self).setUp()
        self.url = reverse('filebrowser:fb_do_upload')
        self.url_bad_name = '?'.join([self.url, urlencode({'folder': self.F_SUBFOLDER.path_relative_directory, 'qqfile': 'TEST IMAGE 000.jpg'})])

        self.client.login(username=self.user.username, password='password')

    def test_post(self):

        uploaded_path = os.path.join(self.F_SUBFOLDER.path, 'testimage.jpg')
        self.assertFalse(site.storage.exists(uploaded_path))

        url = '?'.join([self.url, urlencode({'folder': self.F_SUBFOLDER.path_relative_directory})])

        with open(self.STATIC_IMG_PATH, "rb") as f:
            file_size = os.path.getsize(f.name)
            response = self.client.post(url, data={'qqfile': 'testimage.jpg', 'file': f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Check we get OK response
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.content)
        self.assertEqual(data["filename"], "testimage.jpg")
        self.assertEqual(data["temp_filename"], None)

        # Check the file now exists
        self.testfile = FileObject(uploaded_path, site=site)
        self.assertTrue(site.storage.exists(uploaded_path))

        # Check the file has the correct size
        self.assertTrue(file_size == site.storage.size(uploaded_path))

        # Check permissions
        # TODO: break out into separate test
        if DEFAULT_PERMISSIONS is not None:
            permissions_default = oct(DEFAULT_PERMISSIONS)
            permissions_file = oct(os.stat(self.testfile.path_full).st_mode & 0o777)
            self.assertTrue(permissions_default == permissions_file)

    @patch('filebrowser.sites.UPLOAD_TEMPDIR', '_test/tempfolder')
    def test_do_temp_upload(self):
        """
        Test the temporary upload (used with the FileBrowseUploadField)

        TODO: This is undocumented.
        """

        uploaded_path = os.path.join(self.F_TEMPFOLDER.path, 'testimage.jpg')
        self.assertFalse(site.storage.exists(uploaded_path))

        # TODO: Why is folder required to be temp? Shouldn't it use tempfolder
        # regardless of what is specified?
        url = reverse('filebrowser:fb_do_upload')
        url = '?'.join([url, urlencode({'folder': self.F_TEMPFOLDER.path_relative_directory, 'qqfile': 'testimage.jpg', 'temporary': 'true'})])

        with open(self.STATIC_IMG_PATH, "rb") as f:
            file_size = os.path.getsize(f.name)
            response = self.client.post(url, data={'qqfile': 'testimage.jpg', 'file': f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Check we get OK response
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.content)
        self.assertEqual(data["filename"], "testimage.jpg")
        self.assertEqual(data["temp_filename"], os.path.join(self.F_TEMPFOLDER.path_relative_directory, "testimage.jpg"))

        # Check the file now exists
        self.testfile = FileObject(uploaded_path, site=site)
        self.assertTrue(site.storage.exists(uploaded_path))

        # Check the file has the correct size
        self.assertTrue(file_size == site.storage.size(uploaded_path))

        # Check permissions
        if DEFAULT_PERMISSIONS is not None:
            permissions_default = oct(DEFAULT_PERMISSIONS)
            permissions_file = oct(os.stat(self.testfile.path_full).st_mode & 0o777)
            self.assertTrue(permissions_default == permissions_file)

    @patch('filebrowser.sites.OVERWRITE_EXISTING', True)
    def test_overwrite_existing_true(self):
        shutil.copy(self.STATIC_IMG_PATH, self.SUBFOLDER_PATH)
        self.assertEqual(site.storage.listdir(self.F_SUBFOLDER), ([], [u'testimage.jpg']))

        url = '?'.join([self.url, urlencode({'folder': self.F_SUBFOLDER.path_relative_directory})])

        with open(self.STATIC_IMG_PATH, "rb") as f:
            self.client.post(url, data={'qqfile': 'testimage.jpg', 'file': f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(site.storage.listdir(self.F_SUBFOLDER), ([], [u'testimage.jpg']))

    @patch('filebrowser.sites.OVERWRITE_EXISTING', False)
    def test_overwrite_existing_false(self):
        shutil.copy(self.STATIC_IMG_PATH, self.SUBFOLDER_PATH)
        self.assertEqual(site.storage.listdir(self.F_SUBFOLDER), ([], [u'testimage.jpg']))

        url = '?'.join([self.url, urlencode({'folder': self.F_SUBFOLDER.path_relative_directory})])

        with open(self.STATIC_IMG_PATH, "rb") as f:
            self.client.post(url, data={'qqfile': 'testimage.jpg', 'file': f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(len(site.storage.listdir(self.F_SUBFOLDER)[1]), 2)

    @patch('filebrowser.utils.CONVERT_FILENAME', False)
    @patch('filebrowser.utils.NORMALIZE_FILENAME', False)
    def test_convert_false_normalize_false(self):
        with open(self.STATIC_IMG_BAD_NAME_PATH, "rb") as f:
            self.client.post(self.url_bad_name, data={'qqfile': 'TEST IMAGE 000.jpg', 'file': f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(site.storage.listdir(self.F_SUBFOLDER), ([], [u'TEST IMAGE 000.jpg']))

    @patch('filebrowser.utils.CONVERT_FILENAME', True)
    @patch('filebrowser.utils.NORMALIZE_FILENAME', False)
    def test_convert_true_normalize_false(self):
        with open(self.STATIC_IMG_BAD_NAME_PATH, "rb") as f:
            self.client.post(self.url_bad_name, data={'qqfile': 'TEST IMAGE 000.jpg', 'file': f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(site.storage.listdir(self.F_SUBFOLDER), ([], [u'test_image_000.jpg']))

    @patch('filebrowser.utils.CONVERT_FILENAME', False)
    @patch('filebrowser.utils.NORMALIZE_FILENAME', True)
    def test_convert_false_normalize_true(self):
        with open(self.STATIC_IMG_BAD_NAME_PATH, "rb") as f:
            self.client.post(self.url_bad_name, data={'qqfile': 'TEST IMAGE 000.jpg', 'file': f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(site.storage.listdir(self.F_SUBFOLDER), ([], [u'TEST IMAGE 000.jpg']))

    @patch('filebrowser.utils.CONVERT_FILENAME', True)
    @patch('filebrowser.utils.NORMALIZE_FILENAME', True)
    def test_convert_true_normalize_true(self):
        with open(self.STATIC_IMG_BAD_NAME_PATH, "rb") as f:
            self.client.post(self.url_bad_name, data={'qqfile': 'TEST IMAGE 000.jpg', 'file': f}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(site.storage.listdir(self.F_SUBFOLDER), ([], [u'test_image_000.jpg']))


def test_detail(test):
    """
    Check the detail view and version generation. Check also renaming of files.
    """
    url = reverse('%s:fb_detail' % test.site_name)
    response = test.c.get(url, {'dir': test.testfile.dirname, 'filename': test.testfile.filename})

    # Check we get an OK response for the detail view
    test.assertTrue(response.status_code == 200)

    # At this moment all versions should be generated. Check that.
    pre_rename_versions = []
    for version_suffix in VERSIONS:
        path = test.testfile.version_path(version_suffix)
        pre_rename_versions.append(path)
        test.assertTrue(test.site.storage.exists(path))

    # Attemp renaming the file
    url = '?'.join([url, urlencode({'dir': test.testfile.dirname, 'filename': test.testfile.filename})])
    response = test.c.post(url, {'name': 'testpic.jpg'})

    # Check we get 302 response for renaming
    test.assertTrue(response.status_code == 302)

    # Check the file was renamed correctly:
    test.assertTrue(test.site.storage.exists(os.path.join(test.testfile.head, 'testpic.jpg')))

    # Store the renamed file
    test.testfile = FileObject(os.path.join(test.testfile.head, 'testpic.jpg'), site=test.site)

    # Check if all pre-rename versions were deleted:
    for path in pre_rename_versions:
        test.assertFalse(test.site.storage.exists(path))

    # Check if all post–rename versions were deleted (resp. not being generated):
    for version_suffix in VERSIONS:
        path = test.testfile.version_path(version_suffix)
        test.assertFalse(test.site.storage.exists(path))


def test_delete_confirm(test):
    """
    Check that the delete view functions as expected. Does not check the deletion itself,
    that happens in test_delete().
    """
    url = reverse('%s:fb_delete_confirm' % test.site_name)
    response = test.c.get(url, {'dir': test.testfile.dirname, 'filename': test.testfile.filename})

    # Check we get OK response for delete_confirm
    test.assertTrue(response.status_code == 200)

    # Check the correct template was used
    test.assertTrue('filebrowser/delete_confirm.html' in [t.name for t in response.templates])


def test_delete(test):
    """
    Generate all versions for the uploaded file and attempt a deletion of that file.
    Finally, attempt a deletion of the tmp dir.
    """
    # Generate all versions of the file
    versions = []
    for version_suffix in VERSIONS:
        versions.append(test.testfile.version_generate(version_suffix))

    # Request the delete view
    url = reverse('%s:fb_delete' % test.site_name)
    response = test.c.get(url, {'dir': test.testfile.dirname, 'filename': test.testfile.filename})

    # Check we get 302 response for delete
    test.assertTrue(response.status_code == 302)

    # Check the file and its versions do not exist anymore
    test.assertFalse(test.site.storage.exists(test.testfile.path))
    for version in versions:
        test.assertFalse(test.site.storage.exists(version.path))
    test.testfile = None

    # Delete the tmp dir and check it does not exist anymore
    response = test.c.get(url, {'dir': test.tmpdir.dirname, 'filename': test.tmpdir.filename})
    test.assertTrue(response.status_code == 302)
    test.assertFalse(test.site.storage.exists(test.tmpdir.path))
    test.tmpdir = None
