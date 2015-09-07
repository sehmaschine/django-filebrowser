# coding: utf-8

# PYTHON IMPORTS
import os
import posixpath
import shutil

# DJANGO IMPORTS
from django.conf import settings
from django.test import TestCase
from django.template import Context, Template, TemplateSyntaxError

# FILEBROWSER IMPORTS
import filebrowser
from filebrowser.settings import DEFAULT_PERMISSIONS, STRICT_PIL
from filebrowser.base import FileObject
from filebrowser.sites import site
from filebrowser.utils import scale_and_crop

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image

TESTS_PATH = os.path.dirname(os.path.abspath(__file__))
FILEBROWSER_PATH = os.path.split(TESTS_PATH)[0]


class VersionTemplateTagsTests(TestCase):

    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_path = filebrowser.base.os.path
        self.original_directory = site.directory
        self.original_versions_basedir = filebrowser.base.VERSIONS_BASEDIR
        self.original_versions = filebrowser.base.VERSIONS
        self.original_admin_versions = filebrowser.base.ADMIN_VERSIONS
        self.original_placeholder = filebrowser.templatetags.fb_versions.PLACEHOLDER
        self.original_show_placeholder = filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER
        self.original_force_placeholder = filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER

        # DIRECTORY
        # custom directory because this could be set with sites
        # and we cannot rely on filebrowser.settings
        # FIXME: find better directory name
        self.directory = "fb_test_directory/"
        self.directory_path = os.path.join(site.storage.location, self.directory)
        if os.path.exists(self.directory_path):
            self.fail("Test directory already exists.")
        else:
            os.makedirs(self.directory_path)
        # set site directory
        site.directory = self.directory

        # VERSIONS
        self.versions = "_versionstestdirectory"
        self.versions_path = os.path.join(site.storage.location, self.versions)
        if os.path.exists(self.versions_path):
            self.fail("Versions directory already exists.")
        else:
            os.makedirs(self.versions_path)

        # create temporary test folder and move testimage
        # FIXME: find better path names
        self.tmpdir_name = os.path.join("fb_tmp_dir", "fb_tmp_dir_sub")
        self.tmpdir_path = os.path.join(site.storage.location, self.directory, self.tmpdir_name)
        if os.path.exists(self.tmpdir_path):
            self.fail("Temporary testfolder already exists.")
        else:
            os.makedirs(self.tmpdir_path)

        # copy test image to temporary test folder
        self.image_path = os.path.join(FILEBROWSER_PATH, "static", "filebrowser", "img", "testimage.jpg")
        if not os.path.exists(self.image_path):
            self.fail("Testimage not found.")
        shutil.copy(self.image_path, self.tmpdir_path)

        # create temporary test folder (placeholder) and move testimage
        # FIXME: find better path names
        self.tmpdir_name_ph = os.path.join("fb_tmp_dir", "fb_tmp_placeholder")
        self.tmpdir_path_ph = os.path.join(site.storage.location, self.directory, self.tmpdir_name_ph)
        if os.path.exists(self.tmpdir_path_ph):
            self.fail("Temporary testfolder (placeholder) already exists.")
        else:
            os.makedirs(self.tmpdir_path_ph)

        # copy test image to temporary test folder (placeholder)
        shutil.copy(self.image_path, self.tmpdir_path_ph)

        # set posixpath
        filebrowser.base.os.path = posixpath

        # fileobjects
        self.f_image = FileObject(os.path.join(self.directory, self.tmpdir_name, "testimage.jpg"), site=site)
        self.f_image_not_exists = FileObject(os.path.join(self.directory, self.tmpdir_name, "testimage_does_not_exist.jpg"), site=site)
        self.f_folder = FileObject(os.path.join(self.directory, self.tmpdir_name), site=site)
        self.f_placeholder = FileObject(os.path.join(self.directory, self.tmpdir_name_ph, "testimage.jpg"), site=site)

    def test_scale_crop(self):
        """
        Test scale/crop functionality
        scale_and_crop(im, width, height, opts)

        self.f_image (original): width 1000, height 750
        """

        # new width 500 > 500/375
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 500, "", "")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)
        # new height 375 > 500/375
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, "", 375, "")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

        # SIZE TOO BIG, BUT NO UPSCALE DEFINED

        # new width 1500, no upscale > False
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, "", "")
        self.assertEqual(version, False)
        # new height 1125, no upscale > False
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, "", 1125, "")
        self.assertEqual(version, False)
        # new width 1500, height 1125, no upscale > False
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, 1125, "")
        self.assertEqual(version, False)

        # SIZE TOO BIG, UPSCALE DEFINED

        # new width 1500, upscale > 1500/1125
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, "", "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)
        # new height 1125, upscale > 1500/1125
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, "", 1125, "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)
        # new width 1500, new height 1125, upscale > 1500/1125
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, 1125, "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)
        # new width 1500, new height 1125, upscale > 1500/1125
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, 0, "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)

        # SIZE TOO SMALL, UPSCALE DEFINED

        # width too small, no upscale
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 500, "", "upscale")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)
        # height too small, no upscale
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, "", 375, "upscale")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

        # CROPPING

        # new width 500 and height 500 w. crop > 500/500
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 500, 500, "crop")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 500)
        # new width 1500 and height 1500 w. crop > false (upscale missing)
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, 1500, "crop")
        self.assertEqual(version, False)
        # new width 1500 and height 1500 w. crop > false (upscale missing)
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, 1500, "crop,upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1500)

        # SPECIAL CASES

        # new width 500 and height 1125
        # new width is smaller than original, but new height is bigger
        # width has higher priority
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 500, 1125, "")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)
        # same with upscale
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 500, 1125, "upscale")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)
        # new width 1500 and height 375
        # new width is bigger than original, but new height is smaller
        # height has higher priority
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, 375, "")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)
        # same with upscale
        im = Image.open(self.f_image.path_full)
        version = scale_and_crop(im, 1500, 375, "upscale")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)


    def test_version(self):
        """
        Templatetag version
        """
        # new settings
        filebrowser.base.VERSIONS_BASEDIR = "fb_test_directory/_versions"
        filebrowser.base.VERSIONS = {
            'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
            'large': {'verbose_name': 'Large', 'width': 600, 'height': '', 'opts': ''},
            'fixedheight': {'verbose_name': 'Fixed height', 'width': '', 'height': 100, 'opts': ''},
        }
        filebrowser.base.ADMIN_VERSIONS = ['large']
        filebrowser.settings.VERSIONS = filebrowser.base.VERSIONS
        filebrowser.templatetags.fb_versions.VERSIONS = filebrowser.base.VERSIONS

        # templatetag version with wrong token
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version obj.path %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version %}'))

        # templatetag version without path
        t = Template('{% load fb_versions %}{% version obj "medium" %}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(r, "")  # FIXME: should this throw an error?

        # templatetag version with hardcoded path
        t = Template('{% load fb_versions %}{% version path "large" %}')
        c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # templatetag version with obj
        t = Template('{% load fb_versions %}{% version obj "large" %}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # templatetag version with obj.path
        t = Template('{% load fb_versions %}{% version obj.path "large" %}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # fixed height
        t = Template('{% load fb_versions %}{% version path "fixedheight" %}')
        c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_fixedheight.jpg"))

        # # FIXME: templatetag version with non-existing path
        # t = Template('{% load fb_versions %}{% version path "large" %}')
        # c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimagexxx.jpg"})
        # r = t.render(c)
        # self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # test placeholder with existing image
        filebrowser.templatetags.fb_versions.PLACEHOLDER = "fb_test_directory/fb_tmp_dir/fb_tmp_placeholder/testimage.jpg"
        filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER = True
        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # test placeholder with non-existing image
        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        # Check permissions
        if DEFAULT_PERMISSIONS is not None:
            permissions_default = oct(DEFAULT_PERMISSIONS)
            permissions_file = oct(os.stat(os.path.join(settings.MEDIA_ROOT, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg")).st_mode & 0o777)
            self.assertEqual(permissions_default, permissions_file)

    def test_version_object(self):
        """
        Templatetag version_object
        """
        # new settings
        filebrowser.base.VERSIONS_BASEDIR = "fb_test_directory/_versions"
        filebrowser.base.VERSIONS = {
            'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
            'large': {'verbose_name': 'Large', 'width': 600, 'height': '', 'opts': ''},
        }
        filebrowser.base.ADMIN_VERSIONS = ['large']
        filebrowser.settings.VERSIONS = filebrowser.base.VERSIONS
        filebrowser.templatetags.fb_versions.VERSIONS = filebrowser.base.VERSIONS

        # templatetag with wrong token
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object obj.path %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object obj.path "medium" %}'))

        # templatetag version_object with hardcoded path
        t = Template('{% load fb_versions %}{% version_object path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # templatetag version_object with obj.path
        t = Template('{% load fb_versions %}{% version_object obj.path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # templatetag version_object with obj
        t = Template('{% load fb_versions %}{% version_object obj "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # templatetag version_object with suffix as variable
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # # FIXME: templatetag version with non-existing path
        # t = Template('{% load fb_versions %}{% version_object path "large" as version_large %}{{ version_large.url }}')
        # c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimagexxx.jpg"})
        # r = t.render(c)
        # self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        # self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # test placeholder with existing image
        filebrowser.templatetags.fb_versions.PLACEHOLDER = "fb_test_directory/fb_tmp_dir/fb_tmp_placeholder/testimage.jpg"
        filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER = True
        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # test placeholder with non-existing image
        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

    def test_version_setting(self):
        pass

    def tearDown(self):
        """
        Restore original values/functions
        """
        filebrowser.base.os.path = self.original_path
        site.directory = self.original_directory
        filebrowser.base.VERSIONS_BASEDIR = self.original_versions_basedir
        filebrowser.base.VERSIONS = self.original_versions
        filebrowser.settings.VERSIONS = self.original_versions
        filebrowser.templatetags.fb_versions.VERSIONS = self.original_versions
        filebrowser.base.ADMIN_VERSIONS = self.original_admin_versions
        filebrowser.templatetags.fb_versions.PLACEHOLDER = self.original_placeholder
        filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER = self.original_show_placeholder
        filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER = self.original_force_placeholder

        # remove temporary directory and test folder
        shutil.rmtree(self.directory_path)
        shutil.rmtree(self.versions_path)
