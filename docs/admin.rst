:tocdepth: 2

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser
.. |site| replace:: FileBrowser site
.. |sites| replace:: FileBrowser sites
.. |fb| replace:: FileBrowser

.. _admin:

Admin Interface
===============

The main |filebrowser| admin application is an extension for the Django admin interface in order to browser your media folder, upload and rename/delete files.

.. _site:

FileBrowser Site
----------------

.. class:: FileBrowserSite(name=None, app_name='filebrowser', storage=default_storage)

    Respresents the FileBrowser admin application (similar to Django's admin site).

    :param name: A name for the site, defaults to None.
    :param app_name: Defaults to 'filebrowser'.
    :param storage: A custom storage engine, defaults to Djangos default storage.

Similar to ``django.contrib.admin``, you first need to add a ``filebrowser.site`` to your admin interface. In your ``urls.py``, import the default FileBrowser site (or your custom site) and add the site to your URL-patterns (before any admin-urls)::

    from filebrowser.sites import site

    urlpatterns = patterns('',
       url(r'^adminurl/filebrowser/', include(site.urls)),
    )

Now you are able to browse the location defined with the storage engine associated to your site.

.. code-block:: python

    from django.core.files.storage import DefaultStorage
    from filebrowser.sites import FileBrowserSite

    # Default FileBrowser site
    site = FileBrowserSite(name='filebrowser', storage=DefaultStorage())

    # My Custom FileBrowser site
    custom_site = FileBrowserSite(name='custom_filebrowser', storage=DefaultStorage())
    custom_site.directory = "custom_uploads/"

.. note::
    The module variable ``site`` from ``filebrowser.sites`` is the default FileBrowser application.

.. _actions:

Custom Actions
--------------

Similar to Django's admin actions, you can define your |fb| actions and thus automate the typical tasks of your users. Registered custom actions are listed in the detail view of a file and a user can select a single action at a time. The selected action will then be applied to the file.

The default |fb| image actions, such as "Flip Vertical" or "Rotate 90° Clockwise" are in fact implemented as custom actions (see the module  ``filebrowser.actions``).

Writing Your Own Actions
^^^^^^^^^^^^^^^^^^^^^^^^

Custom actions are simple functions::

    def foo(request, fileobjects):
        # Do something with the fileobjects

The first parameter is a ``HttpRequest`` object (representing the submitted form in which a user selected the action) and the second parameter is a list of ``FileObjects`` to which the action should be applied.

The list contains exactly one instance of FileObject (representing the file from the detail view), but this may change in the future, as custom actions may become available also in browse views (similar to admin actions applied to a list of checked objects).

Registering an Action
^^^^^^^^^^^^^^^^^^^^^

In order to make your action visible, you need to register it with a |site|::

    site.add_action(foo)

Once registered, the action will appear in the detail view of a file. You can also give your action a short description::

    foo.short_description = 'Do foo with the File'

This short description will then appear in the list of available actions. If you do not provide a short description, the function name will be used instead and |fb| will replace any underscores in the function name with spaces.

Associating Actions with Specific Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each custom action can be associated with a specific file type (e.g., images, audio file, etc) to which it applies. In order to do that, you need to define a predicate/filter function, which takes a single argument (FileObject) and returns ``True`` if your action is applicable to that FileObject. Finally, you need to register this filter function with your action::

    foo.applies_to(lambda fileobject: fileobject.filetype == 'Image')

In the above example, foo will appear in the action list only for image files. If you do not specify any filter function for your action, |fb| considers the action as applicable to all files.

Messages & Intermediate Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can provide a feedback to a user about a successful or failed execution of an action by using a message. For example::

    from django.contrib import messages

    def desaturate_image(request, fileobjects):
        for f in fileobjects:
            # Desaturate the image
            messages.add_message(request, messages.SUCCESS, _("Image '%s' was desaturated.") % f.filename)

Some actions may require user confirmation (e.g., in order to prevent accidental and irreversible modification to files). In order to that, follow the same pattern as with Django's admin action and return a ``HttpResponse`` object from your action. Good practice for intermediate pages is to implement a confirm view and have your action return ``HttpResponseRedirect``::

    def crop_image(request, fileobjects):
        files = '&f='.join([f.path_relative for f in fileobjects])
        return HttpResponseRedirect('/confirm/?action=crop_image&f=%s' % files)

.. _storages:

File Storages
-------------

You have the option to specify which file storage engine a |fb| should use to browse/upload/modify your media files. This enables you to use a |fb| even if your media files are located at some remote system. See also the Django's documentation on storages https://docs.djangoproject.com/en/dev/topics/files/.

To associate a |site| with a particular storage engine, set the ``storage`` property of a site object::

    from django.core.files.storage import FileSystemStorage
    site.storage = FileSystemStorage(location='/path/to/media/directory', base_url='/media/')

For storage classes other than FileSystemStorage (or those that inherit from that class), there's more effort involved in providing a storage object that can be used with |fb|. See :ref:`mixin`

.. _mixin:

StorageMixin Class
^^^^^^^^^^^^^^^^^^

A |fb| uses the Django's Storage class to access media files. However, the API of the Storage class does not provide all methods necessary for FileBrowser's functionality. A ``StorageMixin`` class from ``filebrowser.storage`` module therefore defines all the additional methods that a |fb| requires:

.. function:: isdir(self, name)

    Returns true if name exists and is a directory.

.. function:: isfile(self, name)

    Returns true if name exists and is a regular file.

.. function:: move(self, old_file_name, new_file_name, allow_overwrite=False)

    Moves safely a file from one location to another. If ``allow_ovewrite==False`` and ``new_file_name`` exists, raises an exception.

.. function:: makedirs(self, name)

    Creates all missing directories specified by name. Analogue to os.mkdirs().

.. _views:

Views
-----

All views use the ``staff_member_requird`` and ``path_exists`` decorator in order to check if the server path actually exists. Some views also use the ``file_exists`` decorator.

* Browse, ``fb_browse``
    Browse a directory on your server. Returns a :ref:`filelisting`.

    * Optional query string args: ``dir``, ``o``, ``ot``, ``q``, ``p``, ``filter_date``, ``filter_type``, ``type``

* Create directory, ``fb_createdir``
    Create a new folder on your server.

    * Optional query string args: ``dir``
    * Signals: `filebrowser_pre_createdir`, `filebrowser_post_createdir`

* Upload, ``fb_upload``
    Multiple upload.

    * Optional query string args: ``dir``, ``type``
    * Signals: `filebrowser_pre_upload`, `filebrowser_post_upload`

* Edit, ``fb_edit``
    Edit a file or folder.

    * Required query string args: ``filename``
    * Optional query string args: ``dir``
    * Signals: `filebrowser_pre_rename`, `filebrowser_post_rename`

    You are able to apply custom actions (see :ref:`actions`) to the edit-view.

* Confirm delete, ``fb_confirm_delete``
    Confirm the deletion of a file or folder.

    * Required query string args: ``filename``
    * Optional query string args: ``dir``

    If you try to delete a folder, all files/folders within this folder are listed on this page.

* Delete, ``fb_delete``
    Delete a file or folder.

    * Required query string args: ``filename``
    * Optional query string args: ``dir``
    * Signals: `filebrowser_pre_delete`, `filebrowser_post_delete`

.. warning::
    If you delete a Folder, all items within this Folder are being deleted.

* Version, ``fb_version``
    Generate a version of an image as defined with ``ADMIN_VERSIONS``.

    * Required query string args: ``filename``
    * Optional Query string args: ``dir``

    This is a helper used by the ``FileBrowseField`` and TinyMCE for selecting a version.

.. _signals:

Signals
-------

The FileBrowser sends a couple of different signals. Please take a look at the module `filebrowser.signals` for further explanation on the provided arguments.

* :data:`filebrowser_pre_upload`
    Sent before a an Upload starts.

* :data:`filebrowser_post_upload`
    Sent after an Upload has finished.

* :data:`filebrowser_pre_delete`
    Sent before an Item (File, Folder) is deleted.

* :data:`filebrowser_post_delete`
    Sent after an Item (File, Folder) has been deleted.

* :data:`filebrowser_pre_createdir`
    Sent before a new Folder is created.

* :data:`filebrowser_post_createdir`
    Sent after a new Folder has been created.

* :data:`filebrowser_pre_rename`
    Sent before an Item (File, Folder) is renamed.

* :data:`filebrowser_post_rename`
    Sent after an Item (File, Folder) has been renamed.

* :data:`filebrowser_actions_pre_apply`
    Sent before a custom action is applied.

* :data:`filebrowser_actions_post_apply`
    Sent after a custom action has been applied.

.. _signals_examples:

Example for using these Signals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
