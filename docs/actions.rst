:tocdepth: 2

.. |fb| replace:: FileBrowser
.. |site| replace:: FileBrowser site
.. |sites| replace:: FileBrowser sites

.. _actions:

Custom Actions
==============

.. versionadded:: 3.4.0

In analogy to Django's admin actions, you can define your |fb| actions and thus automate the typical tasks of your users. Registered custom actions are listed in the detail view of a file and a user can select a single action at a time. The selected action will then be applied to the file.

The default |fb| image actions, such as "Flip Vertical" or "Rotate 90° Clockwise" are in fact implemented as custom actions (in the module  ``filebrowser.actions``).

Writing Your Own Actions
------------------------

Custom actions are simple functions of the form::

    def foo(request, fileobjects):
        # Do something with the fileobjects

The first parameter is an ``HttpRequest`` object (representing the submitted form in which a user selected the action) and the second parameter is a list of ``FileObjects`` to which the action should be applied.

In the current |fb| version, the list contains exactly one instance of FileObject (representing the file from the detail view), but this may change in the future, as custom actions may become available also in browse views (similar to admin actions applied to a list of checked objects).

Registering an Action
---------------------

In order to make your action visible, you need to register it at a |site| (see also :ref:`sites`)::

    site.add_action(foo)

Once registered, the action will appear in the detail view of a file. You can also give your action a short description::

    foo.short_description = 'Do foo with the File'

This short description will then appear in the list of available actions. If you do not provide any short description for your action, the function name will be used instead and |fb| will replace any underscores in the function name with spaces.

Associating Actions with Specific Files
---------------------------------------

Each custom action can be associated with a specific file type (e.g., images, audio file, etc) to which it applies. In order to do that, you need to define a predicate/filter function, which takes a single argument -- a FileObject -- and returns ``True`` if your action is applicable to that FileObject. Finally, you need to register this filter function with your action::

    foo.applies_to(lambda fileobject: fileobject.filetype == 'Image')

In the above example, foo will appear in the action list only for image files. If you do not specify any filter function for your action, |fb| considers the action as applicable to all files.

Messages & Intermediate Pages
-----------------------------

You can provide a feedback to a user about or successful or failed execution of an action by registering a message at the request object. For example::

    from django.contrib import messages
    
    def desaturate_image(request, fileobjects):
        for f in fileobjects:
            # Desaturate the image
            messages.add_message(request, messages.SUCCESS, _("Image '%s' was desaturated.") % f.filename)

Some actions may require user confirmation (e.g., in order to prevent accidental and irreversible modification to files). In order to that, follow the same pattern as with Django's admin action and return an ``HttpResponse`` object from your action. Good practice for intermediate pages is to implement a confirm view and have your action return an ``HttpResponseRedirect`` object redirecting a user to that view::

    def crop_image(request, fileobjects):
        files = '&f='.join([f.path_relative for f in fileobjects])
        return HttpResponseRedirect('/confirm/?action=crop_image&f=%s' % files)