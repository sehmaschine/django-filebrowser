from setuptools import setup, find_packages

setup(
    name='django-filebrowser',
    version='2.1.0',
    description='File-Management with the Django Admin-Interface.',
    author='Patrick Kranzlmueller',
    author_email='patrick@vonautomatisch.at',
    url='http://code.google.com/p/django-filebrowser/',
    packages=find_packages(),
    package_data = {'filebrowser': ['templates/filebrowser/*.html',
        'templates/filebrowser/include/*',
        'locale/*/LC_MESSAGES/*']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)