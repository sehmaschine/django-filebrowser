from setuptools import setup, find_packages

setup(
    name='django-filebrowser',
    version='3.3.0',
    description='Media-Management with Grappelli',
    author='Patrick Kranzlmueller',
    author_email='patrick@vonautomatisch.at',
    url='https://github.com/sehmaschine/django-filebrowser',
    license = 'BSD',
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
