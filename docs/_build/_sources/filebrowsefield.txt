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

``directory``
    Subdirectory of ``DIRECTORY``. If ``DIRECTORY`` is not defined, subdirectory of ``MEDIA_ROOT``. Do not prepend a slash.

``extensions``
    List of allowed extensions.

``format``
    Use this attribute to restrict selection to specific filetypes. E.g., if you use format='image', only Images can be selected from the FileBrowser. Note: The ``format`` has to be defined within ``SELECT_FORMATS``.

FileBrowseField in Templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When using a ``FileBrowseField``, you´ll get a :ref:`fileobject` back.

With the above Model, you can use::

    {{ blogentry.image }}

to output the contents of your image-field. For example, this could result in something like "uploads/images/myimage.jpg".

Now, if you want to actually display the Image, you write::

    <img src="{{ publication.image }}" />

More complicated, if you want to display "Landscape" Images only (I know, bad example)::

    {% ifequal blogentry.image.image_orientation "landscape" %}
        <img src="{{ blogentry.image }}" class="landscape" />
    {% endifequal %}

Showing Thumbnail in the Changelist
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to show a Thumbnail in the Changelist, you can define a Model-/Admin-Method::

    from filebrowser.settings import ADMIN_THUMBNAIL
    
    def image_thumbnail(self, obj):
        if obj.image and obj.image.filetype == "Image":
            return '<img src="%s" />' % obj.image.version(ADMIN_THUMBNAIL).url
        else:
            return ""
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "Thumbnail"

Using the FileBrowseField with TinyMCE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also replace the TinyMCE Image/File Manager with the FileBrowser. What you have to do is a FileBrowser Callback. There´s an example in /media/js/ called TinyMCEAdmin.js (a TinyMCE Configuration File). You can copy the FileBrowserCallback to your own file, take a look at http://wiki.moxiecode.com/index.php/TinyMCE:Custom_filebrowser or just use TinyMCEAdmin.js.

Just add these lines to your AdminModel::

    class Media:
        js = ['/path/to/tinymce/jscripts/tiny_mce/tiny_mce.js', '/path/to/filebrowser/js/TinyMCEAdmin.js',]

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
    
    def image_upload_fileobject(self):
        if self.image_upload:
            return FileObject(self.image_upload.path)
        return None

To show a Thumbnail on your changelist, you could use a ModelAdmin-Method::
    
    from filebrowser.base import FileObject
    
    def image_upload_thumbnail(self, obj):
        if obj.image_upload:
            image_upload_fileobject = FileObject(obj.image_upload.path)
            if image_upload_fileobject.filetype == "Image":
                return '<img src="%s" />' % image_upload_fileobject.version(ADMIN_THUMBNAIL).url
        else:
            return ""
    image_upload_thumbnail.allow_tags = True
    image_upload_thumbnail.short_description = "Thumbnail"

.. note::
    There's different ways to achive this. The above examples show one of several options.
