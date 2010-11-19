# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-filebrowser-no-grappelli',
    version='3.0',
    description='Media-Management with the Django Admin-Interface. Without the grappelli dependency',
    author='Patrick Kranzlmueller',
    author_email='patrick@vonautomatisch.at',
    contributors=[
        ['Matjaz Crnko', 'matjaz.crnko@gmail.com', 'no-grappelli work'],
    ],
    url='http://code.google.com/p/django-filebrowser/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
