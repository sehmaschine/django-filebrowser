# coding: utf-8
import os
import shutil

from django.conf import settings
from django.test import TestCase
from django.template import Context, Template, TemplateSyntaxError

from filebrowser.settings import STRICT_PIL, DIRECTORY
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

DIRECTORY_PATH = os.path.join(site.storage.location, DIRECTORY)
TEST_PATH = os.path.join(DIRECTORY_PATH, 'filebrowser_test')
PLACEHOLDER_PATH = os.path.join(DIRECTORY_PATH, 'placeholder_test')

STATIC_IMG_PATH = os.path.join(settings.BASE_DIR, 'filebrowser', "static", "filebrowser", "img", "testimage.jpg")
F_IMG = FileObject(os.path.join(DIRECTORY, 'filebrowser_test', "testimage.jpg"), site=site)
F_MISSING = FileObject(os.path.join(DIRECTORY, 'filebrowser_test', "missing.jpg"), site=site)


class ScaleAndCropTests(TestCase):
    def setUp(self):
        os.makedirs(TEST_PATH)
        os.makedirs(PLACEHOLDER_PATH)
        shutil.copy(STATIC_IMG_PATH, TEST_PATH)
        shutil.copy(STATIC_IMG_PATH, PLACEHOLDER_PATH)

        self.im = Image.open(F_IMG.path_full)

    def tearDown(self):
        shutil.rmtree(TEST_PATH)
        shutil.rmtree(PLACEHOLDER_PATH)

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


class VersionTemplateTagTests(TestCase):
    """Test basic version uses

    Eg:
    {% version obj "large" %}
    {% version path "large" %}

    """
    def setUp(self):
        os.makedirs(TEST_PATH)
        os.makedirs(PLACEHOLDER_PATH)

        shutil.copy(STATIC_IMG_PATH, TEST_PATH)
        shutil.copy(STATIC_IMG_PATH, PLACEHOLDER_PATH)

    def tearDown(self):
        shutil.rmtree(TEST_PATH)
        shutil.rmtree(PLACEHOLDER_PATH)

    def test_wrong_token(self):
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version obj.path %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version %}'))

    def test_without_path(self):
        t = Template('{% load fb_versions %}{% version obj "medium" %}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(r, "")  # FIXME: should this throw an error?

    def test_hardcoded_path(self):
        t = Template('{% load fb_versions %}{% version path "large" %}')
        c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_with_obj(self):
        t = Template('{% load fb_versions %}{% version obj "large" %}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_with_obj_path(self):
        t = Template('{% load fb_versions %}{% version obj.path "large" %}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_size_fixedheight(self):
        t = Template('{% load fb_versions %}{% version path "fixedheight" %}')
        c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_fixedheight.jpg"))

        # # FIXME: templatetag version with non-existing path
        # t = Template('{% load fb_versions %}{% version path "large" %}')
        # c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimagexxx.jpg"})
        # r = t.render(c)
        # self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_force_placeholder_with_existing_image(self, ):
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

    def test_force_placeholder_without_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_no_force_placeholder_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

    def test_no_force_placeholder_without_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
    # def test_permissions(self, mock_permissions):
    #     mock_permissions.return_value = 0o755

        # Check permissions
        if DEFAULT_PERMISSIONS is not None:
            permissions_default = oct(DEFAULT_PERMISSIONS)
            permissions_file = oct(os.stat(os.path.join(settings.MEDIA_ROOT, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg")).st_mode & 0o777)
            self.assertEqual(permissions_default, permissions_file)

class VersionAsTemplateTagTests(TestCase):
    """Test variable version uses

    Eg:
    {% version obj "large" as version_large %}
    {% version path "large" as version_large %}

    """

    def setUp(self):
        os.makedirs(TEST_PATH)
        os.makedirs(PLACEHOLDER_PATH)

        shutil.copy(STATIC_IMG_PATH, TEST_PATH)
        shutil.copy(STATIC_IMG_PATH, PLACEHOLDER_PATH)

    def tearDown(self):
        shutil.rmtree(TEST_PATH)
        shutil.rmtree(PLACEHOLDER_PATH)

    def test_hardcoded_path(self):
        t = Template('{% load fb_versions %}{% version path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_obj_path(self):
        t = Template('{% load fb_versions %}{% version obj.path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_with_obj(self):
        t = Template('{% load fb_versions %}{% version obj "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_with_suffix_as_variable(self):
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
    def test_non_existing_path(self):

    def test_force_placeholder_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

    def test_no_force_placeholder_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))


class VersionObjectTemplateTagTests(TestCase):
    """Test version_object uses

    Eg:
    {% version_object obj "large" as version_large %}
    {% version_object path "large" as version_large %}

    """

    def setUp(self):
        os.makedirs(TEST_PATH)
        os.makedirs(PLACEHOLDER_PATH)

        shutil.copy(STATIC_IMG_PATH, TEST_PATH)
        shutil.copy(STATIC_IMG_PATH, PLACEHOLDER_PATH)

    def tearDown(self):
        shutil.rmtree(TEST_PATH)
        shutil.rmtree(PLACEHOLDER_PATH)

    def test_wrong_token(self):
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object obj.path %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object obj.path "medium" %}'))

    def test_hardcoded_path(self):
        t = Template('{% load fb_versions %}{% version_object path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "path": "fb_test_directory/fb_tmp_dir/fb_tmp_dir_sub/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_obj_path(self):
        t = Template('{% load fb_versions %}{% version_object obj.path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_with_obj(self):
        t = Template('{% load fb_versions %}{% version_object obj "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_suffix_as_variable(self):
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
    def test_non_existing_path(self):

    def test_force_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

    def test_no_force_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_dir_sub/testimage_large.jpg"))

    def test_force_with_non_existing_image(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))

    def test_no_force_with_non_existing_image(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.f_image_not_exists, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "fb_test_directory/_versions/fb_tmp_dir/fb_tmp_placeholder/testimage_large.jpg"))
