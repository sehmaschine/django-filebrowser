.. :tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _versions:

Image Versions
==============

With the FileBrowser, you are able to define different versions/sizes for Images. This enables you to save an Original Image on your Server while having different versions of that Image to automatically fit your websites Grid. Versions are also useful for responsive/adaptive layouts.

Versions and the grid
---------------------

First you need to know which versions/sizes of an image you'd like to use on your website. Let's say you're using a 12 column grid with 60px for each column and 20px margin (which is a total of 940px). With this grid, you could (for example) generate these image versions::

      VERSIONS = getattr(settings, "FILEBROWSER_VERSIONS", {
        'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
        'thumbnail': {'verbose_name': 'Thumbnail (1 col)', 'width': 60, 'height': 60, 'opts': 'crop'},
        'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
        'medium': {'verbose_name': 'Medium (4col )', 'width': 300, 'height': '', 'opts': ''},
        'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
        'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''},
      })

.. versionadded:: 3.4.0
    ``methods``

If you need to add some filter for the version (like grayscale, sepia, ...), you can also use the ``methods`` argument::

    def grayscale(im):
        '''Convert the PIL image to grayscale'''
        if im.mode != "L":
            im = im.convert("L")
        return im

    FILEBROWSER_VERSIONS = {
        'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': '', 'methods': [grayscale]},
    })

Versions with the admin-interface
---------------------------------

With the admin-interface, you need to define ``ADMIN_VERSIONS``::

    ADMIN_VERSIONS = getattr(settings, 'FILEBROWSER_ADMIN_VERSIONS', ['thumbnail', 'small', 'medium', 'big', 'large'])

Don't forget to select one version for your admin-thumbnail::

    ADMIN_THUMBNAIL = getattr(settings, 'FILEBROWSER_ADMIN_THUMBNAIL', 'admin_thumbnail')

Versions on your website
------------------------

In order to generate versions, you have two different tags to choose from: ``version`` and ``version_object``. With either using the version-tag or the version_object-tag, the Image-version will be generated "on the fly" if the version doesn't already exist or if the original Image is newer than the version. This means that if you need to update an Image, you just overwrite the original Image - the versions will be re-generated automatically (as you request them within your template).

A Model example::

    from filebrowser.fields import FileBrowseField

    class BlogEntry(models.Model):
        image = FileBrowseField("Image", max_length=200, blank=True, null=True)

First you need to load the templatetags with::

    {% load fb_versions %}

You have two different tags to choose from: ``version`` and ``version_object``.

.. note::
    With both templatetags, ``version_prefix`` can either be a string or a variable. If ``version_prefix`` is a string, use quotes.

Templatetag ``version``
^^^^^^^^^^^^^^^^^^^^^^^

**Generate a version and retrieve the URL**::

    {% version model.field_name version_prefix %}

With the above Model, in order to generate a version you type::

    {% version blogentry.image 'medium' %}

Since you retrieve the URL, you can display the image with::

    <img src="{% version blogentry.image 'medium' %}" />

Templatetag ``version_object``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Generate a version and retrieve the FileObject**::

    {% version_object model.field_name version_prefix as variable %}

With the above Model, in order to generate a version you type::

    {% version_object blogentry.image 'medium' as version_medium %} 

Since you retrieve a ``FileObject``, you can use all attributes::

    {{ version_medium.width }}

or just::

    <img src="{{ version_medium }}" />

Versions in views
-----------------

If you have a ``FileObject`` you can easily generate/retrieve a version with::

    obj.image.version(version_prefix)

So, if you need to generate/retrieve the admin thumbnail for an Image, you can type::

    from filebrowser.settings import ADMIN_THUMBNAIL
    obj.image.version_generate(ADMIN_THUMBNAIL).url

Placeholder
-----------

When developing on a locale machine or a development-server, you might not have all the images (resp. media-files) available that are on your production instance and downloading these files on a regular basis might not be an option.

In that case, you might wanna use a placeholder instead of an image-version. You just need to define the ``PLACEHOLDER`` and overwrite the settings ``SHOW_PLACEHOLDER`` and/or ``FORCE_PLACEHOLDER`` (see :ref:`settingsplaceholder`).

Management Commands
===================

Command ``fb_version_generate``
-------------------------------

If you need to generate certain (or all) versions, type::

    python manage.py fb_version_generate

Command ``fb_version_remove``
-----------------------------

If you need to generate certain (or all) versions, type::

    python manage.py fb_version_remove

.. warning::
    Please be very careful with this command.