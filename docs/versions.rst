.. :tocdepth: 1

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _versions:

Versions
========

With the FileBrowser, you are able to define different versions/sizes for images. This enables you to save an original image on your server while having different versions of that image to automatically fit your websites grid. Versions are also useful for responsive/adaptive layouts.

To generate a version of a source image, you specify `options` which are used
by the image processors (see :ref:`settingsversions_processors`) to generate the
required version.

Defining Versions
-----------------

First you need to know which versions/sizes of an image you'd like to generate
with your website. Let's say you're using a 12 column grid with 60px for each
column and 20px margin (which is a total of 940px). With this grid, you could
(for example) define these image :ref:`settingsversions_versions`:

.. code-block:: python

      FILEBROWSER_VERSIONS_BASEDIR = '_versions'
      FILEBROWSER_VERSIONS = {
        'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
        'thumbnail': {'verbose_name': 'Thumbnail (1 col)', 'width': 60, 'height': 60, 'opts': 'crop'},
        'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
        'medium': {'verbose_name': 'Medium (4col )', 'width': 300, 'height': '', 'opts': ''},
        'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
        'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''},
      }

Use the ``methods`` argument, if you need to add a filter:

.. code-block:: python

    def grayscale(im):
        "Convert image to grayscale"
        if im.mode != "L":
            im = im.convert("L")
        return im

    FILEBROWSER_VERSIONS = {
        'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': '', 'methods': [grayscale]},
    })


.. _versions__custom_processors:

Custom processors
-----------------

.. versionadded:: 3.7.2

Custom processors can be created using a simple method like this:

.. code:: python

    def grayscale_processor(im, grayscale=False, **kwargs):
        if grayscale:
            if im.mode != "L":
                im = im.convert("L")
        return im

The first argument for a processor is the source image.

All other arguments are keyword arguments which relate to the list of options
received from the :ref:`version_generate method <method_version_generate>`.

Ensure that you explicitly declare all params that could be used by your
processor, as the processors arguments can be inspected to get a list of valid
options.

In order to turn your processor optional, define the params that your processor
expects with a falsy default, and in this case you could return the
original image without any modification.

You must also use ``**kwargs`` at the end of your argument list because all
`options` used to generate the version are available to all processors, not
just the ones defined in your processor.

Whether a processor actually modifies the image or not, they must always return
an image.

Using the processor
+++++++++++++++++++

Override the  :ref:`settingsversions_processors` setting:

.. code-block:: python

    FILEBROWSER_VERSION_PROCESSORS = [
        'filebrowser.utils.scale_and_crop',
        'my_project.my_processors.grayscale_processor',
    ]

And in your versions definition:

.. code-block:: python

    FILEBROWSER_VERSIONS = {
        'big_gray': {'verbose_name': 'Big (6 col)', 'width': 460, 'grayscale': True},
    })


Versions and the Admin
----------------------

When using the FileBrowser with the admin interface, you need to define ``ADMIN_VERSIONS`` and ``ADMIN_THUMBNAIL`` (see :ref:`settings`). ``ADMIN_VERSIONS`` are available with the admin, i.e. you are able to see these versions with the image detail view and you are able to select the versions with the :ref:`filebrowsefield` model field.

.. code-block:: python

    FILEBROWSER_ADMIN_VERSIONS = ['thumbnail', 'small', 'medium', 'big', 'large']
    FILEBROWSER_ADMIN_THUMBNAIL = 'admin_thumbnail'

Versions and the Frontend
-------------------------

With the templatetag ``version`` a version will be generated if it doesn't already exist OR if the original image is newer than the version.
In order to update an image, you just overwrite the original image and the versions will be generated automatically (as you request them within your template).

A Model example:

.. code-block:: python

    from filebrowser.fields import FileBrowseField

    class BlogEntry(models.Model):
        image = FileBrowseField("Image", max_length=200, blank=True)

With your templates, use ``version`` if you simply need to retrieve the URL or ``version as var`` if you need to get a :ref:`fileobject`:

.. code-block:: html

    <!-- load filebrowser templatetags -->
    {% load fb_versions %}

    <!-- get the url with version -->
    <img src="{% version blogentry.image 'medium' %}" />

    <!-- get a fileobject with version -->
    {% version blogentry.image 'medium' as version_medium %}
    {{ version_medium.width }}
    <img src="{{ version_medium.url }}" />

Templatetag ``version``
+++++++++++++++++++++++

Retrieves/Generates a version and returns an URL:

.. code-block:: html

    {% version model.field_name version_prefix %}

Retrieves/Generates a version and returns a FileObject:

.. code-block:: html

    {% version model.field_name version_prefix as variable %}

.. note::
    ``version_prefix`` can either be a string or a variable. If ``version_prefix`` is a string, use quotes.

Versions in Views
-----------------

If you have a ``FileObject`` you can generate/retrieve a version with:

.. code-block:: python

    v = obj.image.version_generate(version_prefix) # returns a FileObject

Placeholder
-----------

When developing on a locale machine or a development-server, you might not have all the images (resp. media-files) available that are on your production instance and downloading these files on a regular basis might not be an option.

In that case, you can use a placeholder instead of a version. You just need to define the ``PLACEHOLDER`` and overwrite the settings ``SHOW_PLACEHOLDER`` and/or ``FORCE_PLACEHOLDER`` (see :ref:`settingsplaceholder`).

Management Commands
-------------------

.. option:: fb_version_generate

    If you need to generate certain (or all) versions, type:

    .. code-block:: python

        python manage.py fb_version_generate

.. option:: fb_version_remove

    If you need to remove certain (or all) versions, type:

    .. code-block:: python

        python manage.py fb_version_remove

    .. warning::
        Please be very careful with this command.
