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
from filebrowser.templatetags import fb_versions

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image

DIRECTORY_PATH = os.path.join(site.storage.location, fb_settings.DIRECTORY)
TEST_PATH = os.path.join(DIRECTORY_PATH, 'filebrowser_test')
PLACEHOLDER_PATH = os.path.join(DIRECTORY_PATH, 'placeholder_test')

STATIC_IMG_PATH = os.path.join(settings.BASE_DIR, 'filebrowser', "static", "filebrowser", "img", "testimage.jpg")
F_IMG = FileObject(os.path.join(fb_settings.DIRECTORY, 'filebrowser_test', "testimage.jpg"), site=site)
F_MISSING = FileObject(os.path.join(fb_settings.DIRECTORY, 'filebrowser_test', "missing.jpg"), site=site)


class ScaleAndCropTests(TestCase):
    def setUp(self):
        """
        Save original values/functions so they can be restored in tearDown
        """
        self.original_path = filebrowser.base.os.path
        self.original_directory = site.directory
        self.original_versions_basedir = filebrowser.base.VERSIONS_BASEDIR
        self.original_versions = filebrowser.base.VERSIONS
        self.original_admin_versions = filebrowser.base.ADMIN_VERSIONS
        self.original_placeholder = fb_versions.PLACEHOLDER
        self.original_show_placeholder = fb_versions.SHOW_PLACEHOLDER
        self.original_force_placeholder = fb_versions.FORCE_PLACEHOLDER

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

        self.im = Image.open(F_IMG.path_full)


    def test_scale_width(self):
        version = scale_and_crop(self.im, 500, "", "")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

    def test_scale_height(self):
        # new height 375 > 500/375
        version = scale_and_crop(self.im, "", 375, "")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

    def test_scale_no_upscale_too_wide(self):
        version = scale_and_crop(self.im, 1500, "", "")
        self.assertEqual(version, False)

    def test_scale_no_upscale_too_tall(self):
        version = scale_and_crop(self.im, "", 1125, "")
        self.assertEqual(version, False)

    def test_scale_no_upscale_too_wide_and_tall(self):
        version = scale_and_crop(self.im, 1500, 1125, "")
        self.assertEqual(version, False)

    def test_scale_with_upscale_width(self):
        version = scale_and_crop(self.im, 1500, "", "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)

    def test_scale_with_upscale_height(self):
        version = scale_and_crop(self.im, "", 1125, "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)

    def test_scale_with_upscale_width_and_height(self):
        version = scale_and_crop(self.im, 1500, 1125, "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)

    def test_scale_with_upscale_width_and_zero_height(self):
        version = scale_and_crop(self.im, 1500, 0, "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)

    def test_scale_with_upscale_zero_width_and_height(self):
        version = scale_and_crop(self.im, 0, 1125, "upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1125)

    def test_scale_with_upscale_width_too_small_for_upscale(self):
        version = scale_and_crop(self.im, 500, "", "upscale")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

    def test_scale_with_upscale_height_too_small_for_upscale(self):
        version = scale_and_crop(self.im, "", 375, "upscale")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

    def test_crop_width_and_height(self):
        version = scale_and_crop(self.im, 500, 500, "crop")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 500)

    def test_crop_width_and_height_too_large_no_upscale(self):
        # new width 1500 and height 1500 w. crop > false (upscale missing)
        version = scale_and_crop(self.im, 1500, 1500, "crop")
        self.assertEqual(version, False)

    def test_crop_width_and_height_too_large_with_upscale(self):
        version = scale_and_crop(self.im, 1500, 1500, "crop,upscale")
        self.assertEqual(version.size[0], 1500)
        self.assertEqual(version.size[1], 1500)

    def test_width_smaller_but_height_bigger_no_upscale(self):
        # new width 500 and height 1125
        # new width is smaller than original, but new height is bigger
        # width has higher priority
        version = scale_and_crop(self.im, 500, 1125, "")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

    def test_width_smaller_but_height_bigger_with_upscale(self):
        # same with upscale
        version = scale_and_crop(self.im, 500, 1125, "upscale")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

    def test_width_bigger_but_height_smaller_no_upscale(self):
        # new width 1500 and height 375
        # new width is bigger than original, but new height is smaller
        # height has higher priority
        version = scale_and_crop(self.im, 1500, 375, "")
        self.assertEqual(version.size[0], 500)
        self.assertEqual(version.size[1], 375)

    def test_width_bigger_but_height_smaller_with_upscale(self):
        # same with upscale
        version = scale_and_crop(self.im, 1500, 375, "upscale")
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
        fb_versions.VERSIONS = filebrowser.base.VERSIONS

        # templatetag version with wrong token
class VersionTemplateTagTests(TestCase):
    """Test basic version uses

    Eg:
    {% version obj "large" %}
    {% version path "large" %}

    """
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
        fb_versions.PLACEHOLDER = "fb_test_directory/fb_tmp_dir/fb_tmp_placeholder/testimage.jpg"
        fb_versions.SHOW_PLACEHOLDER = True
        fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # test placeholder with non-existing image
        fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        # Check permissions
        if DEFAULT_PERMISSIONS is not None:
            permissions_default = oct(DEFAULT_PERMISSIONS)
            permissions_file = oct(os.stat(os.path.join(settings.MEDIA_ROOT, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg")).st_mode & 0o777)
            self.assertEqual(permissions_default, permissions_file)

    def test_version_as_object(self):
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
        fb_versions.VERSIONS = filebrowser.base.VERSIONS

        # templatetag version with hardcoded path
class VersionAsTemplateTagTests(TestCase):
    """Test variable version uses

    Eg:
    {% version obj "large" as version_large %}
    {% version path "large" as version_large %}

    """

        t = Template('{% load fb_versions %}{% version path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # templatetag version with obj.path
        t = Template('{% load fb_versions %}{% version obj.path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # templatetag version with obj
        t = Template('{% load fb_versions %}{% version obj "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # templatetag version with suffix as variable
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # # FIXME: templatetag version with non-existing path
        # t = Template('{% load fb_versions %}{% version path "large" as version_large %}{{ version_large.url }}')
        # c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimagexxx.jpg"})
        # r = t.render(c)
        # self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        # self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # test placeholder with existing image
        fb_versions.PLACEHOLDER = "fb_test_directory/fb_tmp_dir/fb_tmp_placeholder/testimage.jpg"
        fb_versions.SHOW_PLACEHOLDER = True
        fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # test placeholder with non-existing image
        fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))


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
        fb_versions.VERSIONS = filebrowser.base.VERSIONS

        # templatetag with wrong token
class VersionObjectTemplateTagTests(TestCase):
    """Test version_object uses

    Eg:
    {% version_object obj "large" as version_large %}
    {% version_object path "large" as version_large %}

    """

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
        fb_versions.PLACEHOLDER = "fb_test_directory/fb_tmp_dir/fb_tmp_placeholder/testimage.jpg"
        fb_versions.SHOW_PLACEHOLDER = True
        fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        fb_versions.FORCE_PLACEHOLDER = False
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        # test placeholder with non-existing image
        fb_versions.FORCE_PLACEHOLDER = True
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        fb_versions.FORCE_PLACEHOLDER = False
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
        fb_versions.VERSIONS = self.original_versions
        filebrowser.base.ADMIN_VERSIONS = self.original_admin_versions
        fb_versions.PLACEHOLDER = self.original_placeholder
        fb_versions.SHOW_PLACEHOLDER = self.original_show_placeholder
        fb_versions.FORCE_PLACEHOLDER = self.original_force_placeholder

        # remove temporary directory and test folder
        shutil.rmtree(self.directory_path)
        shutil.rmtree(self.versions_path)
