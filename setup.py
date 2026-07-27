import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="django-filebrowser",
    version="5.0.0",
    description="Media-Management with Grappelli",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    url="http://django-filebrowser.readthedocs.org",
    download_url="",
    author="Patrick Kranzlmueller, Axel Swoboda (vonautomatisch)",
    author_email="office@vonautomatisch.at",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    zip_safe=False,
    install_requires=[
        "django-grappelli>=4.0,<4.1",
        "pillow",
    ],
)
