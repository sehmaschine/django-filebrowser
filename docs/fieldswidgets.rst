:tocdepth: 2

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

Fields & Widgets
================

The :ref:`filebrowsefield` is a custom model field which returns a :ref:`fileobject`. The widgets :ref:`fileinputwidget` and :ref:`clearablefileinputwidget` are used with the admin app in order to show an additional thumbnail for images.

.. _filebrowsefield:

FileBrowseField
---------------

.. py:class:: FileBrowseField(max_length[, site, directory, extensions, format, **options])

    A subclass of `CharField <https://docs.djangoproject.com/en/1.6/ref/models/fields/#charfield>`_, referencing a media file within.
    Returns a :ref:`fileobject`.

    :param site: A FileBrowser site (defaults to the main site), see :ref:`site`.
    :param directory: Directory to browse when clicking the search icon.
    :param extensions: List of allowed extensions, see :ref:`settingsextensionsformats`.
    :param format: A key from SELECT_FORMATS in order to restrict the selection to specific filetypes, , see :ref:`settingsextensionsformats`.

For example:

.. code-block:: python

    from filebrowser.fields import FileBrowseField
    
    class BlogEntry(models.Model):
        image = FileBrowseField("Image", max_length=200, directory="images/", extensions=[".jpg"], blank=True, null=True)
        document = FileBrowseField("PDF", max_length=200, directory="documents/", extensions=[".pdf",".doc"], blank=True, null=True)

FileBrowseField in Templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use all attributes from :ref:`fileobject`:

.. code-block:: html

    {{ blogentry.image }}
    <img src="{{ publication.image.url }}" />

    {% ifequal blogentry.image.image_orientation "landscape" %}
        <img src="{{ blogentry.image.url }}" class="landscape" />
    {% endifequal %}

Showing Thumbnail in the Changelist
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To show a thumbnail with the changelist, you can define a ModelAdmin method:

.. code-block:: python

    from filebrowser.settings import ADMIN_THUMBNAIL
    
    def image_thumbnail(self, obj):
        if obj.image and obj.image.filetype == "Image":
            return '<img src="%s" />' % obj.image.version_generate(ADMIN_THUMBNAIL).url
        else:
            return ""
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "Thumbnail"

Using the FileBrowseField with TinyMCE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to replace the TinyMCE image/file manager with the FileBrowser, you have to use a `FileBrowser Callback <http://www.tinymce.com/wiki.php/Configuration:file_browser_callback>`_. There's an example TinyMCE configuration file in /static/js/ called TinyMCEAdmin.js. You can either copy the FileBrowserCallback to your own file or just use tinymce_setup.js (which comes with django-grappelli).

Just add these lines to your `ModelAdmin asset definitions <https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#modeladmin-asset-definitions>`_:

.. code-block:: python

    class Media:
        js = ['/path/to/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/path/to/your/tinymce_setup.js']

.. _fileinputwidget:

FileInput
---------

Subclass of `FileInput <https://docs.djangoproject.com/en/1.6/ref/forms/widgets/#fileinput>`_ with an additional thumbnail:

.. code-block:: python
    
    from filebrowser.widgets import FileInput
    
    class BlogEntryOptions(admin.ModelAdmin):
        formfield_overrides = {
            models.ImageField: {'widget': FileInput},
        }

.. _clearablefileinputwidget:

ClearableFileInput
------------------

Subclass of `ClearableFileInput <https://docs.djangoproject.com/en/1.6/ref/forms/widgets/#clearablefileinput>`_ with an additional thumbnail:

.. code-block:: python
    
    from filebrowser.widgets import ClearableFileInput
    
    class BlogEntryOptions(admin.ModelAdmin):
        formfield_overrides = {
            models.ImageField: {'widget': ClearableFileInput},
        }

Django FileField and the FileBrowser
------------------------------------

Return a :ref:`fileobject` from a `FileField <https://docs.djangoproject.com/en/1.6/ref/models/fields/#filefield>`_ or `ImageField <https://docs.djangoproject.com/en/1.6/ref/models/fields/#imagefield>`_ with:

.. code-block:: python
    
    from filebrowser.base import FileObject
    
    image_upload = models.ImageField(u"Image (Upload)", max_length=250, upload_to=image_upload_path, blank=True, null=True)
    
    def image(self):
        if self.image_upload:
            return FileObject(self.image_upload.path)
        return None

In order show a thumbnail with your changelist, you could use a ModelAdmin method:

.. code-block:: python
    
    from filebrowser.base import FileObject
    
    def image_thumbnail(self, obj):
        if obj.image_upload:
            image = FileObject(obj.image_upload.path)
            if image.filetype == "Image":
                return '<img src="%s" />' % image.version_generate(ADMIN_THUMBNAIL).url
        else:
            return ""
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "Thumbnail"

.. note::
    There are different ways to achieve this. The above examples show one of several options.
