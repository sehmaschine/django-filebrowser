.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _quickstart:

Quick start guide
=================

For using the |filebrowser|, `Django <http://www.djangoproject.com>`_ needs to be installed and an `Admin Site <http://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_ has to be activated.

Requirements
------------

* Django 1.4/1.5, http://www.djangoproject.com
* Grappelli 2.4, https://github.com/sehmaschine/django-grappelli
* Pillow, https://github.com/python-imaging/Pillow

Download
--------

Using ``pip``::

    pip install django-filebrowser

Go to https://github.com/sehmaschine/django-filebrowser if you need to download a package or clone the repo.

Installation
------------

.. versionchanged:: 3.4.0

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

Collect the media files::

    python manage.py collectstatic

.. note::
    Please refer to the `Staticfiles Documentation <http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_ for setting up and using ``staticfiles``.

Settings
--------

Check the :ref:`settings`. You need to add a folder "uploads" within ``site.storage.location`` when using the default settings.

Testing
-------

Run the |filebrowser| tests::

    python manage.py test filebrowser

.. warning::
    Please note that the tests will copy files to your filesystem.

Start the devserver and login to your admin site::

    python manage.py runserver <IP-address>:8000

Goto ``/admin/filebrowser/browse/`` and check if everything looks/works as expected. If you're having problems, see :ref:`troubleshooting`.