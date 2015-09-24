# coding: utf-8

import os
import ntpath
import posixpath
import shutil

from mock import patch

from filebrowser.base import FileObject, FileListing
from filebrowser.sites import site
from filebrowser.settings import VERSIONS
from tests import FilebrowserTestCase as TestCase


class FileObjectPathTests(TestCase):

    @patch('filebrowser.base.os.path', ntpath)
    def test_windows_paths(self):
        """
        Use ntpath to test windows paths independently from current os
        """
        f = FileObject('_test\\uploads\\folder\\testfile.jpg', site=site)

        self.assertEqual(f.path_relative_directory, 'folder\\testfile.jpg')
        self.assertEqual(f.dirname, r'folder')

    @patch('filebrowser.base.os.path', posixpath)
    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        f = FileObject('_test/uploads/folder/testfile.jpg', site=site)

        self.assertEqual(f.path_relative_directory, 'folder/testfile.jpg')
        self.assertEqual(f.dirname, r'folder')


class FileObjectUnicodeTests(TestCase):

    @patch('filebrowser.base.os.path', ntpath)
    def test_windows_paths(self):
        """
        Use ntpath to test windows paths independently from current os
        """
        f = FileObject('_test\\uploads\\$%^&*\\測試文件.jpg', site=site)

        self.assertEqual(f.path_relative_directory, '$%^&*\\測試文件.jpg')
        self.assertEqual(f.dirname, r'$%^&*')

    @patch('filebrowser.base.os.path', posixpath)
    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        f = FileObject('_test/uploads/$%^&*/測試文件.jpg', site=site)

        self.assertEqual(f.path_relative_directory, '$%^&*/測試文件.jpg')
        self.assertEqual(f.dirname, r'$%^&*')


class FileObjectAttributeTests(TestCase):

    def test_init_attributes(self):
        """
        FileObject init attributes

        # path
        # head
        # filename
        # filename_lower
        # filename_root
        # extension
        # mimetype
        """
        self.assertEqual(self.F_IMAGE.path, "_test/uploads/folder/testimage.jpg")
        self.assertEqual(self.F_IMAGE.head, '_test/uploads/folder')
        self.assertEqual(self.F_IMAGE.filename, 'testimage.jpg')
        self.assertEqual(self.F_IMAGE.filename_lower, 'testimage.jpg')
        self.assertEqual(self.F_IMAGE.filename_root, 'testimage')
        self.assertEqual(self.F_IMAGE.extension, '.jpg')
        self.assertEqual(self.F_IMAGE.mimetype, ('image/jpeg', None))

    def test_general_attributes(self):
        """
        FileObject general attributes

        # filetype
        # filesize
        # date
        # datetime
        # exists
        """
        self.assertEqual(self.F_IMAGE.filetype, 'Image')

        self.assertEqual(self.F_IMAGE.filetype, 'Image')
        self.assertEqual(self.F_IMAGE.filesize, 870037)
        # FIXME: test date/datetime
        self.assertEqual(self.F_IMAGE.exists, True)

    def test_path_url_attributes(self):
        """
        FileObject path and url attributes

        # path (see init)
        # path_relative_directory
        # path_full
        # dirname
        # url
        """
        # test with image
        self.assertEqual(self.F_IMAGE.path, "_test/uploads/folder/testimage.jpg")
        self.assertEqual(self.F_IMAGE.path_relative_directory, "folder/testimage.jpg")
        self.assertEqual(self.F_IMAGE.path_full, os.path.join(site.storage.location, site.directory, "folder/testimage.jpg"))
        self.assertEqual(self.F_IMAGE.dirname, "folder")
        self.assertEqual(self.F_IMAGE.url, site.storage.url(self.F_IMAGE.path))

        # test with folder
        self.assertEqual(self.F_FOLDER.path, "_test/uploads/folder")
        self.assertEqual(self.F_FOLDER.path_relative_directory, "folder")
        self.assertEqual(self.F_FOLDER.path_full, os.path.join(site.storage.location, site.directory, "folder"))
        self.assertEqual(self.F_FOLDER.dirname, "")
        self.assertEqual(self.F_FOLDER.url, site.storage.url(self.F_FOLDER.path))

        # test with alternative folder
        self.assertEqual(self.F_SUBFOLDER.path, "_test/uploads/folder/subfolder")
        self.assertEqual(self.F_SUBFOLDER.path_relative_directory, "folder/subfolder")
        self.assertEqual(self.F_SUBFOLDER.path_full, os.path.join(site.storage.location, site.directory, "folder/subfolder"))
        self.assertEqual(self.F_SUBFOLDER.dirname, "folder")
        self.assertEqual(self.F_SUBFOLDER.url, site.storage.url(self.F_SUBFOLDER.path))

    def test_image_attributes(self):
        """
        FileObject image attributes

        # dimensions
        # width
        # height
        # aspectratio
        # orientation
        """
        self.assertEqual(self.F_IMAGE.dimensions, (1000, 750))
        self.assertEqual(self.F_IMAGE.width, 1000)
        self.assertEqual(self.F_IMAGE.height, 750)
        self.assertEqual(self.F_IMAGE.aspectratio, 1.3333333333333333)
        self.assertEqual(self.F_IMAGE.orientation, 'Landscape')

    def test_folder_attributes(self):
        """
        FileObject folder attributes

        # directory (deprecated)
        # folder (deprecated)
        # is_folder
        # is_empty
        """
        # test with image
        self.assertEqual(self.F_IMAGE.directory, "folder/testimage.jpg")  # equals path_relative_directory
        self.assertEqual(self.F_IMAGE.folder, "folder")  # equals dirname
        self.assertEqual(self.F_IMAGE.is_folder, False)
        self.assertEqual(self.F_IMAGE.is_empty, False)

        # test with folder
        self.assertEqual(self.F_FOLDER.directory, "folder")  # equals path_relative_directory
        self.assertEqual(self.F_FOLDER.folder, "")  # equals dirname
        self.assertEqual(self.F_FOLDER.is_folder, True)
        self.assertEqual(self.F_FOLDER.is_empty, False)

        # test with alternative folder
        self.assertEqual(self.F_SUBFOLDER.directory, "folder/subfolder")  # equals path_relative_directory
        self.assertEqual(self.F_SUBFOLDER.folder, "folder")  # equals dirname
        self.assertEqual(self.F_SUBFOLDER.is_folder, True)
        self.assertEqual(self.F_SUBFOLDER.is_empty, True)

    @patch('filebrowser.base.ADMIN_VERSIONS', ['large'])
    def test_version_attributes_1(self):
        """
        FileObject version attributes/methods
        without versions_basedir

        # is_version
        # original
        # original_filename
        # versions_basedir
        # versions
        # admin_versions
        # version_name(suffix)
        # version_path(suffix)
        # version_generate(suffix)
        """
        # new settings
        version_list = sorted(['_test/_versions/folder/testimage_{}.jpg'.format(name) for name in VERSIONS.keys()])
        admin_version_list = ['_test/_versions/folder/testimage_large.jpg']

        self.assertEqual(self.F_IMAGE.is_version, False)
        self.assertEqual(self.F_IMAGE.original.path, self.F_IMAGE.path)
        self.assertEqual(self.F_IMAGE.versions_basedir, "_test/_versions/")
        self.assertEqual(self.F_IMAGE.versions(), version_list)
        self.assertEqual(self.F_IMAGE.admin_versions(), admin_version_list)
        self.assertEqual(self.F_IMAGE.version_name("large"), "testimage_large.jpg")
        self.assertEqual(self.F_IMAGE.version_path("large"), "_test/_versions/folder/testimage_large.jpg")

        # version does not exist yet
        f_version = FileObject(os.path.join(site.directory, 'folder', "testimage_large.jpg"), site=site)
        self.assertEqual(f_version.exists, False)
        # generate version
        f_version = self.F_IMAGE.version_generate("large")
        self.assertEqual(f_version.path, "_test/_versions/folder/testimage_large.jpg")
        self.assertEqual(f_version.exists, True)
        self.assertEqual(f_version.is_version, True)
        self.assertEqual(f_version.original_filename, "testimage.jpg")
        self.assertEqual(f_version.original.path, self.F_IMAGE.path)
        # FIXME: versions should not have versions or admin_versions

    @patch('filebrowser.base.ADMIN_VERSIONS', ['large'])
    def test_version_attributes_2(self):
        """
        FileObject version attributes/methods
        with versions_basedir

        # is_version
        # original
        # original_filename
        # versions_basedir
        # versions
        # admin_versions
        # version_name(suffix)
        # version_generate(suffix)
        """

        version_list = sorted(['_test/_versions/folder/testimage_{}.jpg'.format(name) for name in VERSIONS.keys()])
        admin_version_list = ['_test/_versions/folder/testimage_large.jpg']

        self.assertEqual(self.F_IMAGE.is_version, False)
        self.assertEqual(self.F_IMAGE.original.path, self.F_IMAGE.path)
        self.assertEqual(self.F_IMAGE.versions_basedir, "_test/_versions/")
        self.assertEqual(self.F_IMAGE.versions(), version_list)
        self.assertEqual(self.F_IMAGE.admin_versions(), admin_version_list)
        self.assertEqual(self.F_IMAGE.version_name("large"), "testimage_large.jpg")
        self.assertEqual(self.F_IMAGE.version_path("large"), "_test/_versions/folder/testimage_large.jpg")

        # version does not exist yet
        f_version = FileObject(os.path.join(site.directory, 'folder', "testimage_large.jpg"), site=site)
        self.assertEqual(f_version.exists, False)
        # generate version
        f_version = self.F_IMAGE.version_generate("large")
        self.assertEqual(f_version.path, "_test/_versions/folder/testimage_large.jpg")
        self.assertEqual(f_version.exists, True)
        self.assertEqual(f_version.is_version, True)
        self.assertEqual(f_version.original_filename, "testimage.jpg")
        self.assertEqual(f_version.original.path, self.F_IMAGE.path)
        self.assertEqual(f_version.versions(), [])
        self.assertEqual(f_version.admin_versions(), [])

    @patch('filebrowser.base.ADMIN_VERSIONS', ['large'])
    def test_version_attributes_3(self):
        """
        FileObject version attributes/methods
        with alternative versions_basedir

        # is_version
        # original
        # original_filename
        # versions_basedir
        # versions
        # admin_versions
        # version_name(suffix)
        # version_generate(suffix)
        """

        # new settings
        version_list = sorted(['_test/_versions/folder/testimage_{}.jpg'.format(name) for name in VERSIONS.keys()])
        admin_version_list = ['_test/_versions/folder/testimage_large.jpg']

        self.assertEqual(self.F_IMAGE.is_version, False)
        self.assertEqual(self.F_IMAGE.original.path, self.F_IMAGE.path)
        self.assertEqual(self.F_IMAGE.versions_basedir, "_test/_versions/")
        self.assertEqual(self.F_IMAGE.versions(), version_list)
        self.assertEqual(self.F_IMAGE.admin_versions(), admin_version_list)
        self.assertEqual(self.F_IMAGE.version_name("large"), "testimage_large.jpg")
        self.assertEqual(self.F_IMAGE.version_path("large"), "_test/_versions/folder/testimage_large.jpg")

        # version does not exist yet
        f_version = FileObject(os.path.join(site.directory, 'folder', "testimage_large.jpg"), site=site)
        self.assertEqual(f_version.exists, False)
        # generate version
        f_version = self.F_IMAGE.version_generate("large")
        self.assertEqual(f_version.path, "_test/_versions/folder/testimage_large.jpg")
        self.assertEqual(f_version.exists, True)
        self.assertEqual(f_version.is_version, True)
        self.assertEqual(f_version.original_filename, "testimage.jpg")
        self.assertEqual(f_version.original.path, self.F_IMAGE.path)
        self.assertEqual(f_version.versions(), [])
        self.assertEqual(f_version.admin_versions(), [])

    def test_delete(self):
        """
        FileObject delete methods

        # delete
        # delete_versions
        # delete_admin_versions
        """

        # version does not exist yet
        f_version = FileObject(os.path.join(site.directory, 'folder', "testimage_large.jpg"), site=site)
        self.assertEqual(f_version.exists, False)
        # generate version
        f_version = self.F_IMAGE.version_generate("large")
        f_version_thumb = self.F_IMAGE.version_generate("admin_thumbnail")
        self.assertEqual(f_version.exists, True)
        self.assertEqual(f_version_thumb.exists, True)
        self.assertEqual(f_version.path, "_test/_versions/folder/testimage_large.jpg")
        self.assertEqual(f_version_thumb.path, "_test/_versions/folder/testimage_admin_thumbnail.jpg")

        # delete admin versions (large)
        self.F_IMAGE.delete_admin_versions()
        self.assertEqual(site.storage.exists(f_version.path), False)

        # delete versions (admin_thumbnail)
        self.F_IMAGE.delete_versions()
        self.assertEqual(site.storage.exists(f_version_thumb.path), False)


class FileListingTests(TestCase):

    def test_init_attributes(self):
        """
        FileListing init attributes

        # path
        # filter_func
        # sorting_by
        # sorting_order
        """
        self.assertEqual(self.f_listing.path, 'fb_test_directory/')
        self.assertEqual(self.f_listing.filter_func, None)
        self.assertEqual(self.f_listing.sorting_by, 'date')
        self.assertEqual(self.f_listing.sorting_order, 'desc')

    def test_listing(self):
        """
        FileObject listing

        # listing
        # files_listing_total
        # files_listing_filtered
        # results_listing_total
        # results_listing_filtered
        """
        self.assertEqual(self.f_listing_file.listing(), [])
        self.assertEqual(list(self.f_listing.listing()), [u'fb_tmp_dir', u'testimage.jpg'])
        self.assertEqual(list(f.path for f in self.f_listing.files_listing_total()), [u'fb_test_directory/testimage.jpg', u'fb_test_directory/fb_tmp_dir'])
        self.assertEqual(list(f.path for f in self.f_listing.files_listing_filtered()), [u'fb_test_directory/testimage.jpg', u'fb_test_directory/fb_tmp_dir'])
        self.assertEqual(self.f_listing.results_listing_total(), 2)
        self.assertEqual(self.f_listing.results_listing_filtered(), 2)

    def test_listing_filtered(self):
        """
        FileObject listing

        # listing
        # files_listing_total
        # files_listing_filtered
        # results_listing_total
        # results_listing_filtered
        """
        self.assertEqual(self.f_listing_file.listing(), [])
        self.assertEqual(list(self.f_listing.listing()), [u'fb_tmp_dir', u'testimage.jpg'])
        self.assertEqual(list(f.path for f in self.f_listing.files_listing_total()), [u'fb_test_directory/testimage.jpg', u'fb_test_directory/fb_tmp_dir'])
        self.assertEqual(list(f.path for f in self.f_listing.files_listing_filtered()), [u'fb_test_directory/testimage.jpg', u'fb_test_directory/fb_tmp_dir'])
        self.assertEqual(self.f_listing.results_listing_total(), 2)
        self.assertEqual(self.f_listing.results_listing_filtered(), 2)

    def test_walk(self):
        """
        FileObject walk

        # walk
        # files_walk_total
        # files_walk_filtered
        # results_walk_total
        # results_walk_filtered
        """
        self.assertEqual(self.f_listing_file.walk(), [])
        self.assertEqual(list(self.f_listing.walk()), [u'fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg', u'fb_tmp_dir/fb_tmp_dir_sub', u'fb_tmp_dir', u'testimage.jpg'])
        self.assertEqual(list(f.path for f in self.f_listing.files_walk_total()), [u'fb_test_directory/testimage.jpg', u'fb_test_directory/fb_tmp_dir', u'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub', u'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg'])
        self.assertEqual(list(f.path for f in self.f_listing.files_walk_filtered()), [u'fb_test_directory/testimage.jpg', u'fb_test_directory/fb_tmp_dir', u'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub', u'fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg'])
        self.assertEqual(self.f_listing.results_walk_total(), 4)
        self.assertEqual(self.f_listing.results_walk_filtered(), 4)
