:tocdepth: 2

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _filebrowsefield:

FileBrowseField
===============

The ``FileBrowseField`` is a ``Model field`` for selecting a file from your Media Server::

    from filebrowser.fields import FileBrowseField
    
    class BlogEntry(models.Model):
        
        image = FileBrowseField("Image", max_length=200, directory="images/", extensions=[".jpg"], blank=True, null=True)
        document = FileBrowseField("PDF", max_length=200, directory="documents/", extensions=[".pdf",".doc"], blank=True, null=True)
        ...

Attributes
^^^^^^^^^^

``max_length``
    Since the ``FileBrowseField`` is a ``CharField``, you have to define ``max_length``.

``site`` (optional)
    The FileBrowser site you want to use with this field. Defaults to the main site, if not given.

``directory`` (optional)
    Subdirectory of ``site.directory``. If ``site.directory`` is not defined, subdirectory of ``site.storage.location``. Do not prepend a slash.

``extensions`` (optional)
    List of allowed extensions.

``format`` (optional)
    Use this attribute to restrict selection to specific filetypes. E.g., if you use format='image', only Images can be selected from the FileBrowser. Note: The ``format`` has to be defined within ``SELECT_FORMATS``.

FileBrowseField in Templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When using a ``FileBrowseField``, you'll get a :ref:`fileobject` back.

With the above Model, you can use::

    {{ blogentry.image }}

to output the contents of your image-field. For example, this could result in something like "myimage.jpg".

Now, if you want to actually display the Image, you write::

    <img src="{{ publication.image.url }}" />

More complicated, if you want to display "Landscape" Images only::

    {% ifequal blogentry.image.image_orientation "landscape" %}
        <img src="{{ blogentry.image.url }}" class="landscape" />
    {% endifequal %}

Showing Thumbnail in the Changelist
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to show a Thumbnail in the Changelist, you can define a Model-/Admin-Method::

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

You can also replace the TinyMCE Image/File Manager with the FileBrowser. What you have to do is a FileBrowser Callback. There's an example in /media/js/ called TinyMCEAdmin.js (a TinyMCE Configuration File). You can copy the FileBrowserCallback to your own file, take a look at http://www.tinymce.com/wiki.php/Configuration:file_browser_callback or just use tinymce_setup.js (which comes with django-grappelli).

Just add these lines to your AdminModel::

    class Media:
        js = ['/path/to/tinymce/jscripts/tiny_mce/tiny_mce.js', '/path/to/your/tinymce_setup.js',]

FileInput
=========

Subclass of ``FileInput`` with an additional Image-Thumbnail::
    
    from filebrowser.widgets import FileInput
    
    class BlogEntryOptions(admin.ModelAdmin):
        formfield_overrides = {
            models.ImageField: {'widget': FileInput},
        }

ClearableFileInput
==================

Subclass of ``ClearableFileInput`` with an additional Image-Thumbnail::
    
    from filebrowser.widgets import ClearableFileInput
    
    class BlogEntryOptions(admin.ModelAdmin):
        formfield_overrides = {
            models.ImageField: {'widget': ClearableFileInput},
        }

Django ``FileField`` and the FileBrowser
========================================

Generate a ``FileObject`` from a ``FileField`` or ``ImageField`` with::
    
    from filebrowser.base import FileObject
    
    image_upload = models.ImageField(u"Image (Upload)", max_length=250, upload_to=image_upload_path, blank=True, null=True)
    
    def image(self):
        if self.image_upload:
            return FileObject(self.image_upload.path)
        return None

To show a Thumbnail on your changelist, you could use a ModelAdmin-Method::
    
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
