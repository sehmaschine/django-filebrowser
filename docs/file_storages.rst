:tocdepth: 2

.. |site| replace:: FileBrowser site
.. |sites| replace:: FileBrowser sites
.. |fb| replace:: FileBrowser

.. _storages:

File Storages
=============

.. versionadded:: 3.4.0

Starting with |fb| 3.4, you have the option to specify which file storage engine a |fb| should use to browse/upload/modify your media files. This enables you to use a |fb| even if your media files are located at some remote system. See also the Django's documentation on storages https://docs.djangoproject.com/en/dev/topics/files/.

To associate a |site| with a particular storage, set the ``storage`` property of a site object::

	from django.core.files.storage import FileSystemStorage
	site.storage = FileSystemStorage(location='/path/to/media/directory', base_url='/media/')

For storage classes other than FileSystemStorage (or those that inherit from that class), there's a little bit more effort involved in providing a storage object that can be used with |fb|. See :ref:`mixin`

.. note::
	Prior |fb| 3.4, the way to specify |fb|'s  MEDIA_ROOT and MEDIA_URL was via ``settings.py``. Starting from version 3.4, those variables are associated with the storage instance and you can set them as illustrated in the above example. 

.. warning::
	For the reason of backward compatibility, |fb| settings ``FILEBROWSER_MEDIA_ROOT`` and ``FILEBROWSER_MEDIA_URL`` can still be used to customize |fb| as long as you're using the default |fb|'s site without having changed its storage engine. In the next major release of |fb| these settings will be removed.


.. _mixin:

StorageMixin Class
------------------

A |fb| uses the Django's Storage class to access media files. However, the API of the Storage class does not provide all methods necessary for FileBrowser's functionality. A ``StorageMixin`` class from ``filebrowser.storage`` module therefore defines all the additional methods that a |fb| requires:

.. function:: isdir(self, name):

	Returns true if name exists and is a directory.

.. function:: isfile(self, name):
        
	Returns true if name exists and is a regular file.

.. function:: move(self, old_file_name, new_file_name, allow_overwrite=False):
        
    Moves safely a file from one location to another.
	If ``allow_ovewrite==False`` and *new_file_name* exists, raises an exception.        

.. function:: makedirs(self, name):
        
    Creates all missing directories specified by name. Analogue to os.mkdirs().
        

.. function:: rmtree(self, name):
        
    Deletes a directory and everything it contains. Analogue to shutil.rmtree().
            

.. note::
	|fb| provides these methods only for FileSystemStorage (by mixing-in the ``filebrowser.storage.FileSystemStorageMixin`` class). If you're using a custom storage engine, which does not inherit from Django's FileSystemStorage, you will need to provide those method yourself. 