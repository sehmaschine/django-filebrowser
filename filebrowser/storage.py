# coding: utf-8
import os, shutil

from django.core.files.move import file_move_safe
from django.core.files.storage import FileSystemStorage, DefaultStorage
from django.core.files.base import ContentFile

class StorageMixin(object):
    """
    Adds some useful methods to the Storage class.
    """

    def isdir(self, path):
        dirname, basename = os.path.split(path)
        if not basename: # path ends with a slash (probably a directory, but let's be sure..)
            dirname = os.path.dirname(dirname)
            basename = os.path.relpath(path, dirname) # Gets rid of the trailing slash
        dirs, files = self.listdir(dirname)
        return basename in dirs

    def isfile(self, path):
        dirname, basename = os.path.split(path)
        if not basename: # path ends with a slash (probably a directory, but let's be sure..)
            dirname = os.path.dirname(dirname)
            basename = os.path.relpath(path, dirname) # Gets rid of the trailing slash
        dirs, files = self.listdir(dirname)
        return basename in files

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        """
        Moves safely a file from one location to another.

        If allow_ovewrite==False and old_file_name exists, raises an exception.
        """
        raise NotImplementedError()
        # tmpfile = None
        # if self.exists(new_file_name):
        #     if not allow_overwrite:
        #         raise 'File already exists. Try: allow_overwrite=True'
        #     else:
        #         # Make a temporary copy of the file that gets overwritten
        #         try:
        #             tmpfile = self.open(new_file_name)
        #             tmpfile_name = self.save(new_file_name, tmpfile)
        #         finally:
        #             tmpfile.close()
        #         # Delete the original file
        #         self.delete(new_file_name)                
        # # Copy the old file to the new location and delete the old one
        # try:
        #     old_file = self.open(old_file_name)
        #     self.save(new_file_name, old_file)
        # finally:
        #     old_file.close()
        # # Delete the old file
        # self.delete(old_file_name)
        # # Delete tmpfile if created
        # if tmpfile:
        #     self.delete(tmpfile_name)


    def rename(self, old_file_name, new_file_name):
        """
        Rename a file. See note at file_move_safe()
        """
        raise NotImplementedError()

    def makedirs(self, name):
        """
        Creates all missing directories specified by name. Analogue to os.mkdirs().
        """
        raise NotImplementedError()
        # if self.isfile(name):
        #     raise IOError('%s exists and is a file.' % name)
        # f = ContentFile('') # empty file
        # # We assume that self.save() creates dirs as necessary
        # filename = self.save(os.path.join(name, 'tmp'), f)
        # self.delete(os.path.join(name, 'tmp'))
        # if not self.exists(name):
        #     raise IOError('Failed to create dir %s' % name)

    def rmtree(self, name):
        """
        Deletes a directory and everything it contains. Analogue to shutil.rmtree().
        """
        raise NotImplementedError()

class FileSystemStorageMixin(StorageMixin):

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        file_move_safe(self.path(old_file_name), self.path(new_file_name), allow_overwrite=True)

    def rename(self, old_file_name, new_file_name):
        os.rename(self.path(old_file_name), self.path(new_file_name))
    
    def makedirs(self, name):
        os.makedirs(self.path(name))

    def rmtree(self, name):
        shutil.rmtree(self.path(name))