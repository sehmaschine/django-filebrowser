.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _quickstart:

Quick start guide
=================

For using the |filebrowser|, `Django <http://www.djangoproject.com>`_ needs to be installed and an `Admin Site <http://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_ has to be activated.

Requirements
------------

* Django 1.4/1.5/1.6/1.7, http://www.djangoproject.com
* Grappelli 2.4/2.5/2.6, https://github.com/sehmaschine/django-grappelli
* Pillow, https://github.com/python-imaging/Pillow

Installation
------------

Install the |filebrowser|:

.. code-block:: console

    pip install django-filebrowser

Add the filebrowser to your ``INSTALLED_APPS`` (before django.contrib.admin):

.. code-block:: python

    INSTALLED_APPS = (
        'grappelli',
        'filebrowser',
        'django.contrib.admin',
    )

Add the |filebrowser| site to your url-patterns (before any admin-urls):

.. code-block:: python

    from filebrowser.sites import site
    
    urlpatterns = patterns('',
       (r'^admin/filebrowser/', include(site.urls)),
       (r'^grappelli/', include('grappelli.urls')),
       (r'^admin/', include(admin.site.urls)),
    )

Collect the static files (please refer to the `Staticfiles Documentation <http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_ for more information):

.. code-block:: console

    python manage.py collectstatic

Settings
--------

Check the :ref:`settings`.

.. note::
    You need to add a folder "uploads" within ``site.storage.location`` when using the default settings. And we strongly recommend to define a ``VERSIONS_BASEDIR``.

Testing
-------

Run the |filebrowser| tests:

.. code-block:: console

    python manage.py test filebrowser

.. warning::
    Please note that the tests will copy files to your filesystem.

Start the devserver and login to your admin site:

.. code-block:: console

    python manage.py runserver <IP-address>:8000

Goto /admin/filebrowser/browse/ and check if everything looks/works as expected. If you're having problems, see :ref:`troubleshooting`.