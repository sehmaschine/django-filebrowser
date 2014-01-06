:orphan:

.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _troubleshooting:

Troubleshooting
===============

Check your setup
^^^^^^^^^^^^^^^^

Please check if the problem is caused by your setup.

* Read :ref:`quickstart`.
* Check if the static/media-files are served correctly.
* Make sure you have removed all custom |filebrowser| templates from all locations in ``TEMPLATE_DIRS`` or check that these templates are compatible with the |filebrowser|.

Run the tests
^^^^^^^^^^^^^

Start the shell and type:

.. code-block:: console

    python manage.py test filebrowser

.. warning::
    Please note that the tests will copy files to your filesystem.

Check issues
^^^^^^^^^^^^

If your setup is fine, please check if your problem is a known issue.

* Take a look at all `FileBrowser Issues <https://github.com/sehmaschine/django-filebrowser/issues>`_ (incuding closed) and search the `FileBrowser Google-Group <http://groups.google.com/group/django-filebrowser>`_.

Add a ticket
^^^^^^^^^^^^

If you think you've found a bug, please `add a ticket <https://github.com/sehmaschine/django-filebrowser/issues>`_.

* Try to describe your problem as precisely as possible.
* Tell us what you did in order to solve the problem.
* Tell us what version of the |filebrowser| you are using.
* Tell us what version of Django you are using.
* Please do NOT add tickets if you're having problems with serving static/media-files (because this is not related to the |filebrowser|).
* Please do NOT add tickets referring to Djangos trunk version.
* At best: add a patch.

.. note::
    Be aware that we may close issues not following these guidlines without further notifications.