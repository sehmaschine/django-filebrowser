:tocdepth: 2

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _views:

Adding Sites
============

Similar to ``django.contrib.admin``, you first need to add a ``filebrowser.site`` to your admin interface.

In your ``urls.py`` import the default FileBrowser site (or your custom site)::

    from filebrowser.sites import site

and add the site to your URL-patterns (before any admin-urls)::
    
    urlpatterns = patterns('',
       url(r'^adminurl/filebrowser/', include(site.urls)),
    )

Now you are able to browse the location defined with the storage engine associated to your site.

Views
=====

All views use the ``staff_member_requird`` and ``path_exists`` decorator in order to check if the server path actually exists. Some views also use the ``file_exists`` decorator.

Browse
------

Browse a directory on your server. Returns a :ref:`filelisting`::

    /adminurl/filebrowser/browse/

* URL: ``fb_browse``
* Optional query string args: ``dir``, ``o``, ``ot``, ``q``, ``p``, ``filter_date``, ``filter_type``, ``type``

.. _views_createdir:

Create directory
----------------

Create a new folder on your server::

    /adminurl/filebrowser/createdir/

* URL: ``fb_createdir``
* Optional query string args: ``dir``
* Signals: :ref:`filebrowser_pre_createdir`, :ref:`filebrowser_post_createdir`

.. _views_upload:

Upload
------

Multiple upload::

    /adminurl/filebrowser/upload/

* URL: ``fb_upload``
* Optional query string args: ``dir``
* Signals: :ref:`filebrowser_pre_upload`, :ref:`filebrowser_post_upload`

.. _views_edit:

Edit
----

Edit a file or folder::

    /adminurl/filebrowser/edit/?filename=testimage.jpg

* URL: ``fb_edit``
* Required query string args: ``filename``
* Optional query string args: ``dir``
* Signals: :ref:`filebrowser_pre_rename`, :ref:`filebrowser_post_rename`

You are able to apply custom actions (see :ref:`actions`) to the edit-view.

.. note::
    This won't check if you use the file or folder anywhere with your models.

.. _views_confirm_delete:

Confirm delete
--------------

Confirm the deletion of a file or folder::

    /adminurl/filebrowser/confirm_delete/?filename=testimage.jpg

* URL: ``fb_confirm_delete``
* Required query string args: ``filename``
* Optional query string args: ``dir``

.. note::
    If you try to delete a folder, all files/folders within this folder are listed on this page.

.. _views_delete:

Delete
------

Delete a file or folder::

    /adminurl/filebrowser/delete/?filename=testimage.jpg

* URL: ``fb_delete``
* Required query string args: ``filename``
* Optional query string args: ``dir``
* Signals: :ref:`filebrowser_pre_delete`, :ref:`filebrowser_post_delete`

.. note::
    This won't check if you use the file or folder anywhere with your models.

.. warning::
    If you delete a Folder, all items within this Folder are being deleted.

.. _views_version:

Version
-------

Generate a version of an Image as defined with ``ADMIN_VERSIONS``::

    /adminurl/filebrowser/version/?filename=testimage.jpg

* URL: ``fb_version``
* Required query string args: ``filename``
* Query string args: ``dir``

.. note::
    This is a helper used by the ``FileBrowseField`` and TinyMCE for selecting an Image-Version.

.. _signals:

Signals
=======

The FileBrowser sends a couple of different signals:

.. _filebrowser_pre_upload:

``filebrowser_pre_upload``
--------------------------

Sent before a an Upload starts. Arguments:

* ``path``: Absolute server path to the file/folder
* ``name``: Name of the file/folder
* ``site``: Current ``FileBrowserSite`` instance

.. _filebrowser_post_upload:

``filebrowser_post_upload``
---------------------------

Sent after an Upload has finished. Arguments:

* ``path``: Absolute server path to the file/folder
* ``name``: Name of the file/folder
* ``site``: Current ``FileBrowserSite`` instance

.. _filebrowser_pre_delete:

``filebrowser_pre_delete``
--------------------------

Sent before an Item (File, Folder) is deleted. Arguments:

* ``path``: Absolute server path to the file/folder
* ``name``: Name of the file/folder
* ``site``: Current ``FileBrowserSite`` instance

.. _filebrowser_post_delete:

``filebrowser_post_delete``
---------------------------

Sent after an Item (File, Folder) has been deleted. Arguments:

* ``path``: Absolute server path to the file/folder
* ``name``: Name of the file/folder
* ``site``: Current ``FileBrowserSite`` instance

.. _filebrowser_pre_createdir:

``filebrowser_pre_createdir``
-----------------------------

Sent before a new Folder is created. Arguments:

* ``path``: Absolute server path to the folder
* ``name``: Name of the new folder
* ``site``: Current ``FileBrowserSite`` instance

.. _filebrowser_post_createdir:

``filebrowser_post_createdir``
------------------------------

Sent after a new Folder has been created. Arguments:

* ``path``: Absolute server path to the folder
* ``name``: Name of the new folder
* ``site``: Current ``FileBrowserSite`` instance

.. _filebrowser_pre_rename:

``filebrowser_pre_rename``
--------------------------

Sent before an Item (File, Folder) is renamed. Arguments:

* ``path``: Absolute server path to the file/folder
* ``name``: Name of the file/folder
* ``new_name``: New name of the file/folder
* ``site``: Current ``FileBrowserSite`` instance

.. _filebrowser_post_rename:

``filebrowser_post_rename``
---------------------------

Sent after an Item (File, Folder) has been renamed.

* ``path``: Absolute server path to the file/folder
* ``name``: Name of the file/folder
* ``new_name``: New name of the file/folder
* ``site``: Current ``FileBrowserSite`` instance

``filebrowser_actions_pre_apply``
---------------------------------

Sent before a custom action is applied. Arguments:

* ``action_name``: Name of the custom action
* ``fileobjects``: A list of fileobjects the action will be applied to
* ``site``: Current ``FileBrowserSite`` instance

``filebrowser_actions_post_apply``
----------------------------------

Sent after a custom action has been applied.

* ``action_name``: Name of the custom action
* ``fileobjects``: A list of fileobjects the action has been be applied to
* ``results``: The response you defined with your custom action
* ``site``: Current ``FileBrowserSite`` instance

.. _signals_examples:

Example for using these Signals
-------------------------------

Here's a small example for using the above Signals::

    from filebrowser import signals
    
    def pre_upload_callback(sender, **kwargs):
        """
        Receiver function called before an upload starts.
        """
        print "Pre Upload Callback"
        print "kwargs:", kwargs
    signals.filebrowser_pre_upload.connect(pre_upload_callback)
    
    def post_upload_callback(sender, **kwargs):
        """
        Receiver function called each time an upload has finished.
        """
        print "Post Upload Callback"
        print "kwargs:", kwargs
        # You can use all attributes available with the FileObject
        # This is just an example ...
        print "Filesize:", kwargs['file'].filesize
        print "Orientation:", kwargs['file'].orientation
        print "Extension:", kwargs['file'].extension
    signals.filebrowser_post_upload.connect(post_upload_callback)