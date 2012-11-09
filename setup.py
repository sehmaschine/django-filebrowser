import os
import codecs
from setuptools import setup, find_packages

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-filebrowser',
    version='3.5.2',
    description='Media-Management with Grappelli',
    long_description = read('README.rst'),
    author='Patrick Kranzlmueller, Axel Swoboda, Vaclav Mikolasek (vonautomatisch)',
    author_email='office@vonautomatisch.at',
    url = 'http://django-filebrowser.readthedocs.org',
    download_url='',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe = False,
    install_requires = [
        'django-grappelli>=2.4,<2.4.99',
    ],
)