# coding: utf-8

"""
Tests for FileBrowser sites and their views. 

Note that we *dynamically generate* test cases for each deployed FileBrowser site. 
This includes creation of TestCase subclasses at runtime and also creation of 
instance methods from functions.
"""

# PYTHON IMPORTS
import os
import sys
import shutil
from urllib import urlencode
from types import MethodType

# DJANGO IMPORTS
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import get_resolver, get_urlconf, resolve, reverse

# FILEBROWSER IMPORTS
from filebrowser.core.settings import *
from filebrowser.core.base import FileObject
from filebrowser.core.sites import get_site_dict
from filebrowser.core.functions import get_version_path

# This module will test all FileBrowser sites with the following app_name
APP_NAME = 'filebrowser.core'

### TEST FUNCTIONS

def test_browse(test):
    """
    Check the browse view functions as expected.
    """
    url = reverse('%s:fb_browse' % test.site_name)
    response = test.c.get(url)
    
    # Check we get OK response for browsing
    test.assertTrue(response.status_code == 200)
    
    # Check that a correct template was used:
    test.assertTrue('filebrowser/core/index.html' in [t.name for t in response.templates])
    
    # Check directory was set correctly in the context. If this fails, it may indicate
    # that two sites were instantiated with the same name.
    test.assertTrue(test.site.directory == response.context['site'].directory)

def test_createdir(test):
    """
    Check the createdir view functions as expected. Creates a new tmp directory
    under 'site.directory'.
    """
    # Generate a name of a new temp directory
    prefix = 'tmp_test'
    sufix = 0
    tmpdir_name = '%s_%d' % (prefix, sufix)
    while test.site.storage.exists(os.path.join(test.site.directory, tmpdir_name)):
        sufix += 1
        tmpdir_name = '%s_%d' % (prefix, sufix)
    
    # Store the this temp directory (we need to delete it later)
    test.tmpdir = FileObject(os.path.join(test.site.directory, tmpdir_name), site=test.site)
    
    # Create the directory using the createdir view
    url = reverse('%s:fb_createdir' % test.site_name)
    response = test.c.post(url,{'name' : tmpdir_name})
    
    # Check we got Redirection response for createdir
    test.assertTrue(response.status_code == 302)
    
    # Check the directory now exists
    test.assertTrue(test.site.storage.exists(test.tmpdir.path))

def test_upload(test):
    """
    Check the upload view functions as expected. Does not check the uploading itself.
    """
    url = reverse('%s:fb_upload' % test.site_name)
    response = test.c.get(url, {'name': test.tmpdir.path_relative_directory})
    
    # Check we get OK response for upload view
    test.assertTrue(response.status_code == 200)
    
    # Check the correct template was used
    test.assertTrue('filebrowser/core/upload.html' in [t.name for t in response.templates])

def test_do_upload(test):
    ## Attemp an upload using AJAX SUBMISSION
    f = open(os.path.join(PATH_FILEBROWSER_MEDIA, 'img/testimage.jpg'), "rb")
    file_size = os.path.getsize(f.name)
    url = reverse('%s:fb_do_upload' % test.site_name)
    url = '?'.join([url, urlencode({'folder': test.tmpdir.path_relative_directory, 'qqfile': 'testimage.jpg'})])
    response = test.c.post(url, data=f.read(), content_type='application/octet-stream', HTTP_X_REQUESTED_WITH='XMLHttpRequest', X_File_Name='testimage.jpg')
    f.close()
    
    # Check we get OK response
    test.assertTrue(response.status_code == 200)
    
    # Check the file now exists
    path = os.path.join(test.tmpdir.path, 'testimage.jpg')
    test.testfile = FileObject(path, site=test.site)
    test.assertTrue(test.site.storage.exists(path))
    
    # Check the file has the correct size
    test.assertTrue(file_size == test.site.storage.size(path))
    
    # ## Attemp an upload of the file using BASIC SUBMISSION
    # f = open(os.path.join(PATH_FILEBROWSER_MEDIA, 'img/testimage.jpg'))
    # url = reverse('%s:fb_do_upload' % test.site_name)
    # response = test.c.post(url, {'file':f, 'folder': test.tmpdir.path_relative_directory, 'file_name': 'testimage_basic.jpg'})
    # f.close()
    
    # # Check we get OK response
    # test.assertTrue(response.status_code == 200)
    
    # # Check the file now exists
    # abs_path = os.path.join(test.tmpdir.path, 'testimage_basic.jpg')
    # test.assertTrue(test.site.storage.exists(abs_path))
    
    # # Check the file has the correct size
    # test.assertTrue(file_size == os.path.getsize(abs_path))

def test_detail(test):
    """
    Check the detail view and version generation. Check also renaming of files.
    """
    url = reverse('%s:fb_detail' % test.site_name)
    response = test.c.get(url, {'dir': test.testfile.folder, 'filename': test.testfile.filename})
    
    # Check we get an OK response for the detail view
    test.assertTrue(response.status_code == 200)
        
    # Attemp renaming the file
    url = '?'.join([url, urlencode({'dir': test.testfile.folder, 'filename': test.testfile.filename})])
    response = test.c.post(url, {'name': 'testpic.jpg'})
    
    # Check we get 302 response for renaming
    test.assertTrue(response.status_code == 302)
    
    # Check the file was renamed correctly:
    test.assertTrue(test.site.storage.exists(os.path.join(test.testfile.head, 'testpic.jpg')))
    
    # Store the renamed file
    test.testfile = FileObject(os.path.join(test.testfile.head, 'testpic.jpg'), site=test.site)


def test_delete_confirm(test):
    """
    Check that the delete view functions as expected. Does not check the deletion itself, 
    that happens in test_delete().
    """
    url = reverse('%s:fb_delete_confirm' % test.site_name)
    response = test.c.get(url, {'dir': test.testfile.folder, 'filename': test.testfile.filename})
    
    # Check we get OK response for delete_confirm
    test.assertTrue(response.status_code == 200)
    
    # Check the correct template was used
    test.assertTrue('filebrowser/core/delete_confirm.html' in [t.name for t in response.templates])

def test_delete(test):
    """
    Generate all versions for the uploaded file and attempt a deletion of that file.
    Finally, attempt a deletion of the tmp dir.
    """
    
    # Request the delete view
    url = reverse('%s:fb_delete' % test.site_name)
    response = test.c.get(url, {'dir': test.testfile.folder, 'filename': test.testfile.filename})

    # Check we get 302 response for delete
    test.assertTrue(response.status_code == 302)
    
    # Check the file and its versions do not exist anymore
    test.assertFalse(test.site.storage.exists(test.testfile.path))
    test.testfile = None

    # Delete the tmp dir and check it does not exist anymore
    response = test.c.get(url, {'dir': test.tmpdir.folder, 'filename': test.tmpdir.filename})
    test.assertTrue(response.status_code == 302)
    test.assertFalse(test.site.storage.exists(test.tmpdir.path))
    test.tmpdir = None


### INSTANCE METHODS

## setUp, tearDown, and runTest methods for the dynamically created 
## test cases (they will become instance methods)

def setUp(self):
    # Create a site_tester user
    from django.contrib.auth.models import User
    user = User.objects.create_user('site_tester', 'st@willworkforfood.com', 'secret')
    user.is_staff = True
    user.save()
    # Obtain the site object
    self.site = get_site_dict(APP_NAME)[self.site_name]

def tearDown(self):
    # Delete a left-over tmp directories, if there's any
    if self.tmpdir:
        print "Removing left-over tmp dir:", self.tmpdir.path
        self.site.storage.rmtree(self.tmpdir.path)

def runTest(self):
    # Login
    response = self.c.login(username='site_tester', password='secret')
    self.assertTrue(response)
    # Execute tests
    test_browse(self)
    test_createdir(self)
    test_upload(self)
    test_do_upload(self)
    test_detail(self)
    test_delete_confirm(self)
    test_delete(self)

### CREATION OF TEST CASES

# Get the names of all deployed filebrowser sites with the given
all_sites = get_resolver(get_urlconf()).app_dict[APP_NAME]

this_module = sys.modules[__name__]

## Create a test class for each deployed filebrowser site        
for site in all_sites:
    print 'Creating Test for the FileBrowser site:', site
    # Create a subclass of TestCase
    testcase_class = type('TestSite_' + site, (TestCase,), {'site_name': site, 'c': Client(), 'tmpdirs': None})
    # Add setUp, tearDown, and runTest methods
    setattr(testcase_class, 'setUp', MethodType(setUp, None, testcase_class))
    setattr(testcase_class, 'tearDown', MethodType(tearDown, None, testcase_class))
    setattr(testcase_class, 'runTest', MethodType(runTest, None, testcase_class))
    # Add the test case class to this module
    setattr(this_module, 'TestSite_' + site, testcase_class)

# Delete the attribute test_class, otherwise it will be 
# considered as a test case by django 
delattr(this_module, 'testcase_class')
