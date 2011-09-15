.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _quickstart:

Quick start guide
=================

For using the |filebrowser|, `Django <http://www.djangoproject.com>`_ needs to be installed and an `Admin Site <http://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_ has to be activated.

Requirements
------------

* Django 1.3, http://www.djangoproject.com
* Grappelli 2.3, https://github.com/sehmaschine/django-grappelli
* PIL, http://www.pythonware.com/products/pil/

Download
--------

Using ``pip``::

    pip install django-filebrowser

Go to https://github.com/sehmaschine/django-filebrowser if you need to download a package or clone the repo.

Installation
------------

.. versionchanged:: 3.4

Open ``settings.py`` and add ``filebrowser`` to your ``INSTALLED_APPS`` (before ``django.contrib.admin``)::

    INSTALLED_APPS = (
        'grappelli',
        'filebrowser',
        'django.contrib.admin',
    )

In your ``url.py`` import the default FileBrowser site::

    from filebrowser.sites import site

and add the following URL-patterns (before any admin-urls)::
    
    urlpatterns = patterns('',
       url(r'^admin/filebrowser/', include(site.urls)),
    )

.. note:: (Setting up URLs with versions prior to FileBrowser 3.4)

    Skip the import from filebrowser.sites and add the URL-patterns (before any admin-urls) like this::

        urlpatterns = patterns('',
            (r'^admin/filebrowser/', include(filebrowser.urls)),
        )

Collect the media files::

    python manage.py collectstatic

.. note::
    Please refer to the `Staticfiles Documentation <http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_ for setting up and using ``staticfiles``.

If you're not using ``staticfiles`` you can either use a symlink from your media-directory (given by ``MEDIA_ROOT`` and ``MEDIA_URL``) or copy the filebrowser media-files to your media-directory. Don't forget to change the ``settings`` accordingly.

Testing
-------

Run the |filebrowser| tests::

    python manage.py test filebrowser

Start the devserver and login to your admin site::

    python manage.py runserver <IP-address>:8000

Goto ``/admin/filebrowser/browse/`` and check if everything looks/works as expected. If you're having problems, see :ref:`troubleshooting`.
