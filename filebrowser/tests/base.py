# coding: utf-8

# PYTHON IMPORTS
import os
import ntpath
import posixpath

# DJANGO IMPORTS
from django.test import TestCase
from django.contrib.auth.models import User

# PYTHON IMPORTS
from filebrowser.settings import *
import filebrowser
from filebrowser.base import FileObject


class FileObjectPathTests(TestCase):
    
    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_media_root = filebrowser.base.MEDIA_ROOT
        self.original_directory = filebrowser.base.DIRECTORY
        self.original_media_url = filebrowser.base.MEDIA_URL
        self.original_path = filebrowser.base.os.path
    
    # def test_windows_paths(self):
    #     """
    #     Use ntpath to test windows paths independently from current os
    #     """
    #     filebrowser.base.os.path = ntpath
    #     filebrowser.base.MEDIA_ROOT = 'C:\\path\\to\\media\\'
    #     filebrowser.base.DIRECTORY = 'uploads/'
    #     filebrowser.base.MEDIA_URL = '/media/'
    #     f = FileObject('C:\\path\\to\\media\\uploads\\testdir\\testfile.jpg')
    #     
    #     self.assertEqual(f.path_relative, 'uploads\\testdir\\testfile.jpg')
    #     self.assertEqual(f.path_relative_directory, 'testdir\\testfile.jpg')
    #     self.assertEqual(f.directory, 'testdir\\testfile.jpg')
    #     self.assertEqual(f.folder, r'testdir')
    #     
    #     self.assertEqual(f.url, '/media/uploads/testdir/testfile.jpg')
    #     self.assertEqual(f.url_relative, 'uploads/testdir/testfile.jpg')
    
    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        filebrowser.base.os.path = posixpath
        filebrowser.base.MEDIA_ROOT = '/path/to/media/'
        filebrowser.base.DIRECTORY = 'uploads/'
        filebrowser.base.MEDIA_URL = '/media/'
        f = FileObject('/path/to/media/uploads/testdir/testfile.jpg')
        
        self.assertEqual(f.path_relative, 'uploads/testdir/testfile.jpg')
        self.assertEqual(f.path_relative_directory, 'testdir/testfile.jpg')
        self.assertEqual(f.directory, 'testdir/testfile.jpg')
        self.assertEqual(f.folder, r'testdir')
        
        self.assertEqual(f.url, '/media/uploads/testdir/testfile.jpg')
        self.assertEqual(f.url_relative, 'uploads/testdir/testfile.jpg')
    
    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.MEDIA_ROOT = self.original_media_root
        filebrowser.base.DIRECTORY = self.original_directory
        filebrowser.base.MEDIA_URL = self.original_media_url
        filebrowser.base.os.path = self.original_path


class FileObjectVersionTests(TestCase):

    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_media_root = filebrowser.base.MEDIA_ROOT
        self.original_directory = filebrowser.base.DIRECTORY
        self.original_media_url = filebrowser.base.MEDIA_URL
        self.original_path = filebrowser.base.os.path
    
    # def test_windows_paths(self):
    #     """
    #     Use ntpath to test windows paths independently from current os
    #     """
    #     filebrowser.base.os.path = ntpath
    #     filebrowser.base.MEDIA_ROOT = 'C:\\path\\to\\media\\'
    #     filebrowser.base.DIRECTORY = 'uploads/'
    #     filebrowser.base.MEDIA_URL = '/media/'
    #     f = FileObject('C:\\path\\to\\media\\uploads\\testdir\\testfile.jpg')
    #     
    #     self.assertEqual(f.path_relative, 'uploads\\testdir\\testfile.jpg')
    #     self.assertEqual(f.path_relative_directory, 'testdir\\testfile.jpg')
    #     self.assertEqual(f.directory, 'testdir\\testfile.jpg')
    #     self.assertEqual(f.folder, r'testdir')
    #     
    #     self.assertEqual(f.url, '/media/uploads/testdir/testfile.jpg')
    #     self.assertEqual(f.url_relative, 'uploads/testdir/testfile.jpg')
    
    def test_posix_paths(self):
        """
        Use posixpath to test posix paths independently from current os
        """
        filebrowser.base.os.path = posixpath
        filebrowser.base.MEDIA_ROOT = '/path/to/media/'
        filebrowser.base.DIRECTORY = 'uploads/'
        filebrowser.base.MEDIA_URL = '/media/'
        f = FileObject('/path/to/media/uploads/testdir/testfile.jpg')
        
        self.assertEqual(f.path_relative, 'uploads/testdir/testfile.jpg')
        self.assertEqual(f.path_relative_directory, 'testdir/testfile.jpg')
        self.assertEqual(f.directory, 'testdir/testfile.jpg')
        self.assertEqual(f.folder, r'testdir')
        
        self.assertEqual(f.url, '/media/uploads/testdir/testfile.jpg')
        self.assertEqual(f.url_relative, 'uploads/testdir/testfile.jpg')
    
    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.MEDIA_ROOT = self.original_media_root
        filebrowser.base.DIRECTORY = self.original_directory
        filebrowser.base.MEDIA_URL = self.original_media_url
        filebrowser.base.os.path = self.original_path


