# coding: utf-8

# PYTHON IMPORTS
import os
import ntpath
import posixpath

# DJANGO IMPORTS
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.encoding import filepath_to_uri

# FILEBROWSER IMPORTS
from filebrowser.settings import *
import filebrowser
from filebrowser.base import FileObject
from filebrowser.sites import site


class FileObjectPathTests(TestCase):
    
    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_directory = site.directory
        self.original_media_url = filebrowser.base.MEDIA_URL
        self.original_path = filebrowser.base.os.path
    
    def test_windows_paths(self):
        """
        Use ntpath to test windows paths independently from current os
        """
        site.directory = 'uploads/'
        filebrowser.base.os.path = ntpath
        filebrowser.base.MEDIA_URL = '/media/'
        f = FileObject('uploads\\testdir\\testfile.jpg', site=site)
        
        self.assertEqual(f.path_relative_directory, 'testdir\\testfile.jpg')
        self.assertEqual(f.directory, 'testdir\\testfile.jpg')
        self.assertEqual(f.folder, r'testdir')
        
        
    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        filebrowser.base.os.path = posixpath
        site.directory = 'uploads/'
        filebrowser.base.MEDIA_URL = '/media/'
        f = FileObject('uploads/testdir/testfile.jpg', site=site)
        
        self.assertEqual(f.path_relative_directory, 'testdir/testfile.jpg')
        self.assertEqual(f.directory, 'testdir/testfile.jpg')
        self.assertEqual(f.folder, r'testdir')
        
        
    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.MEDIA_URL = self.original_media_url
        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory


class FileObjectUnicodeTests(TestCase):
    
    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_path = filebrowser.base.os.path
        self.original_directory = site.directory
        self.original_media_url = filebrowser.base.MEDIA_URL
    
    def test_windows_paths(self):
        """
        Use ntpath to test windows paths independently from current os
        """
        site.directory = 'uploads/'
        filebrowser.base.os.path = ntpath
        filebrowser.base.MEDIA_URL = '/media/'
        f = FileObject('uploads\\$%^&*\\測試文件.jpg', site=site)
        
        self.assertEqual(f.path_relative_directory, '$%^&*\\測試文件.jpg')
        self.assertEqual(f.directory, '$%^&*\\測試文件.jpg')
        self.assertEqual(f.folder, r'$%^&*')
        
        
    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        filebrowser.base.os.path = posixpath
        site.directory = 'uploads/'
        filebrowser.base.MEDIA_URL = '/media/'
        f = FileObject('uploads/$%^&*/測試文件.jpg', site=site)
        
        self.assertEqual(f.path_relative_directory, '$%^&*/測試文件.jpg')
        self.assertEqual(f.directory, '$%^&*/測試文件.jpg')
        self.assertEqual(f.folder, r'$%^&*')
        
        
    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.MEDIA_URL = self.original_media_url
        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory


class FileObjectVersionTests(TestCase):
    
    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_path = filebrowser.base.os.path
        self.original_directory = site.directory
        self.original_media_url = filebrowser.base.MEDIA_URL
    
    def test_windows_paths(self):
        """
        Use ntpath to test windows paths independently from current os
        """
        site.directory = 'uploads/'
        filebrowser.base.os.path = ntpath
        filebrowser.base.MEDIA_URL = '/media/'
        f = FileObject('uploads\\testdir\\testfile.jpg', site=site)
        
        self.assertEqual(f.path_relative_directory, 'testdir\\testfile.jpg')
        self.assertEqual(f.directory, 'testdir\\testfile.jpg')
        self.assertEqual(f.folder, r'testdir')
        
    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        filebrowser.base.os.path = posixpath
        site.directory = 'uploads/'
        filebrowser.base.MEDIA_URL = '/media/'
        f = FileObject('uploads/testdir/testfile.jpg', site=site)
        
        self.assertEqual(f.path_relative_directory, 'testdir/testfile.jpg')
        self.assertEqual(f.directory, 'testdir/testfile.jpg')
        self.assertEqual(f.folder, r'testdir')
        
    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.MEDIA_URL = self.original_media_url
        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory
        


