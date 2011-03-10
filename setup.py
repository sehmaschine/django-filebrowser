from setuptools import setup, find_packages

setup(
    name='django-filebrowser',
    version='3.2',
    description='Media-Management with the Django Admin-Interface.',
    author='Patrick Kranzlmueller (vonautomatisch)',
    author_email='werkstaetten@vonautomatisch.at',
    url='http://code.google.com/p/django-filebrowser/',
    download_url='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
