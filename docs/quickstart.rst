.. |grappelli| replace:: Grappelli
.. |filebrowser| replace:: FileBrowser

.. _quickstart:

Quick start guide
=================

For using the |filebrowser|, `Django <http://www.djangoproject.com>`_ needs to be installed and an `Admin Site <http://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_ has to be activated.

Requirements
------------

* Python 3.6+
* Django 3.0, http://www.djangoproject.com
* Grappelli 2.14, https://github.com/sehmaschine/django-grappelli
* Pillow, https://github.com/python-imaging/Pillow

Installation
------------

Install the |filebrowser|:

.. code-block:: console

    pip install django-filebrowser

Add the filebrowser to your ``INSTALLED_APPS`` (before django.contrib.admin):

.. code-block:: python

    INSTALLED_APPS = [
        'grappelli',
        'filebrowser',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]

Add the |filebrowser| site to your url-patterns (before any admin-urls):

.. code-block:: python

    from django.contrib import admin
    from django.urls import path
    from django.urls import include
    from filebrowser.sites import site
    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = [
        path('admin/filebrowser/', site.urls),
        path('grappelli/', include('grappelli.urls')),
        path('admin/', admin.site.urls),
    ]

    # only for development server. File serving will be automatically disabled when DEBUG=False
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Make sure you defined Django settings for media and static files (please refer to the `Settings Documentation <https://docs.djangoproject.com/en/dev/ref/settings/>`_ for more information):

.. code-block:: python

    # recommended values for media and static files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")

Collect the static files (please refer to the `Staticfiles Documentation <http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_ for more information):

.. code-block:: console

    python manage.py collectstatic

Settings
--------

Check the :ref:`settings`.

.. note::
    You need to add a folder "uploads" within ``site.storage.location`` when using the default settings.

Testing
-------

Start the devserver and login to your admin site:

.. code-block:: console

    python manage.py runserver <IP-address>:8000

Goto /admin/filebrowser/browse/ and check if everything looks/works as expected. If you're having problems, see :ref:`troubleshooting`.
