from setuptools import setup, find_packages

setup(
    name='django-filebrowser',
    version='development',
    description='Media-Management with the Django Admin-Interface.',
    author='Patrick Kranzlmueller',
    author_email='patrick@vonautomatisch.at',
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
