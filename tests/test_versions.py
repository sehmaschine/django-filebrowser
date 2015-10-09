# coding: utf-8
import os
import shutil

from django.conf import settings
from django.template import Context, Template, TemplateSyntaxError
from mock import patch

from tests import FilebrowserTestCase as TestCase
from filebrowser.settings import STRICT_PIL
from filebrowser.utils import scale_and_crop

if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


class ScaleAndCropTests(TestCase):
    def setUp(self):
        super(ScaleAndCropTests, self).setUp()
        shutil.copy(self.STATIC_IMG_PATH, self.FOLDER_PATH)

        self.im = Image.open(self.F_IMAGE.path_full)

    def test_scale_width(self):
        version = scale_and_crop(self.im, 500, "", "")
        self.assertEqual(version.size, (500, 375))

    def test_scale_height(self):
        # new height 375 > 500/375
        version = scale_and_crop(self.im, "", 375, "")
        self.assertEqual(version.size, (500, 375))

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
        self.assertEqual(version.size, (1500, 1125))

    def test_scale_with_upscale_height(self):
        version = scale_and_crop(self.im, "", 1125, "upscale")
        self.assertEqual(version.size, (1500, 1125))

    def test_scale_with_upscale_width_and_height(self):
        version = scale_and_crop(self.im, 1500, 1125, "upscale")
        self.assertEqual(version.size, (1500, 1125))

    def test_scale_with_upscale_width_and_zero_height(self):
        version = scale_and_crop(self.im, 1500, 0, "upscale")
        self.assertEqual(version.size, (1500, 1125))

    def test_scale_with_upscale_zero_width_and_height(self):
        version = scale_and_crop(self.im, 0, 1125, "upscale")
        self.assertEqual(version.size, (1500, 1125))

    def test_scale_with_upscale_width_too_small_for_upscale(self):
        version = scale_and_crop(self.im, 500, "", "upscale")
        self.assertEqual(version.size, (500, 375))

    def test_scale_with_upscale_height_too_small_for_upscale(self):
        version = scale_and_crop(self.im, "", 375, "upscale")
        self.assertEqual(version.size, (500, 375))

    def test_crop_width_and_height(self):
        version = scale_and_crop(self.im, 500, 500, "crop")
        self.assertEqual(version.size, (500, 500))

    def test_crop_width_and_height_too_large_no_upscale(self):
        # new width 1500 and height 1500 w. crop > false (upscale missing)
        version = scale_and_crop(self.im, 1500, 1500, "crop")
        self.assertEqual(version, False)

    def test_crop_width_and_height_too_large_with_upscale(self):
        version = scale_and_crop(self.im, 1500, 1500, "crop,upscale")
        self.assertEqual(version.size, (1500, 1500))

    def test_width_smaller_but_height_bigger_no_upscale(self):
        # new width 500 and height 1125
        # new width is smaller than original, but new height is bigger
        # width has higher priority
        version = scale_and_crop(self.im, 500, 1125, "")
        self.assertEqual(version.size, (500, 375))

    def test_width_smaller_but_height_bigger_with_upscale(self):
        # same with upscale
        version = scale_and_crop(self.im, 500, 1125, "upscale")
        self.assertEqual(version.size, (500, 375))

    def test_width_bigger_but_height_smaller_no_upscale(self):
        # new width 1500 and height 375
        # new width is bigger than original, but new height is smaller
        # height has higher priority
        version = scale_and_crop(self.im, 1500, 375, "")
        self.assertEqual(version.size, (500, 375))

    def test_width_bigger_but_height_smaller_with_upscale(self):
        # same with upscale
        version = scale_and_crop(self.im, 1500, 375, "upscale")
        self.assertEqual(version.size, (500, 375))


class VersionTemplateTagTests(TestCase):
    """Test basic version uses

    Eg:
    {% version obj "large" %}
    {% version path "large" %}

    """

    def setUp(self):
        super(VersionTemplateTagTests, self).setUp()
        shutil.copy(self.STATIC_IMG_PATH, self.FOLDER_PATH)

        os.makedirs(self.PLACEHOLDER_PATH)
        shutil.copy(self.STATIC_IMG_PATH, self.PLACEHOLDER_PATH)

    def test_wrong_token(self):
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version obj.path %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version %}'))

    def test_invalid_version(self):
        # FIXME: should this throw an error?
        t = Template('{% load fb_versions %}{% version obj "invalid" %}')
        c = Context({"obj": self.F_IMAGE})
        r = t.render(c)
        self.assertEqual(r, "")

    def test_hardcoded_path(self):
        t = Template('{% load fb_versions %}{% version path "large" %}')
        c = Context({"obj": self.F_IMAGE, "path": "_test/uploads/folder/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_with_obj(self):
        t = Template('{% load fb_versions %}{% version obj "large" %}')
        c = Context({"obj": self.F_IMAGE})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_with_obj_path(self):
        t = Template('{% load fb_versions %}{% version obj.path "large" %}')
        c = Context({"obj": self.F_IMAGE})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    @patch.dict('filebrowser.templatetags.fb_versions.VERSIONS', {'fixedheight': {'verbose_name': 'Fixed height', 'width': '', 'height': 100, 'opts': ''}})
    def test_size_fixedheight(self):
        t = Template('{% load fb_versions %}{% version path "fixedheight" %}')
        c = Context({"obj": self.F_IMAGE, "path": "_test/uploads/folder/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_fixedheight.jpg"))

    def test_non_existing_path(self):
        # FIXME: templatetag version with non-existing path
        t = Template('{% load fb_versions %}{% version path "large" %}')
        c = Context({"obj": self.F_IMAGE, "path": "_test/uploads/folder/testimagexxx.jpg"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, ""))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    @patch('filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER', True)
    def test_force_placeholder_with_existing_image(self, ):
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.F_IMAGE, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    @patch('filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER', True)
    def test_force_placeholder_without_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.F_MISSING, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    def test_no_force_placeholder_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.F_IMAGE, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    def test_no_force_placeholder_without_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj.path suffix %}')
        c = Context({"obj": self.F_MISSING, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))

    # def test_permissions(self):
    # FIXME: Test permissions by creating file AFTER we patch DEFAULT_PERMISSIONS
    #     permissions_file = oct(os.stat(os.path.join(settings.MEDIA_ROOT, "_test/_versions/folder/testimage_large.jpg")).st_mode & 0o777)
    #     self.assertEqual(oct(0o755), permissions_file)


class VersionAsTemplateTagTests(TestCase):
    """Test variable version uses

    Eg:
    {% version obj "large" as version_large %}
    {% version path "large" as version_large %}

    """

    def setUp(self):
        super(VersionAsTemplateTagTests, self).setUp()
        shutil.copy(self.STATIC_IMG_PATH, self.FOLDER_PATH)

        os.makedirs(self.PLACEHOLDER_PATH)
        shutil.copy(self.STATIC_IMG_PATH, self.PLACEHOLDER_PATH)

    def test_hardcoded_path(self):
        t = Template('{% load fb_versions %}{% version path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "path": "_test/uploads/folder/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_obj_path(self):
        t = Template('{% load fb_versions %}{% version obj.path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_with_obj(self):
        t = Template('{% load fb_versions %}{% version obj "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_with_suffix_as_variable(self):
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_non_existing_path(self):
        # FIXME: templatetag version with non-existing path
        t = Template('{% load fb_versions %}{% version path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "path": "_test/uploads/folder/testimagexxx.jpg"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, ""))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, ""))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    @patch('filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER', True)
    def test_force_placeholder_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    def test_no_force_placeholder_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    @patch('filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER', True)
    def test_force_placeholder_with_non_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_MISSING, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    def test_no_force_placeholder_with_non_existing_image(self):
        t = Template('{% load fb_versions %}{% version obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_MISSING, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))


class VersionObjectTemplateTagTests(TestCase):
    """Test version_object uses

    Eg:
    {% version_object obj "large" as version_large %}
    {% version_object path "large" as version_large %}

    """
    def setUp(self):
        super(VersionObjectTemplateTagTests, self).setUp()
        shutil.copy(self.STATIC_IMG_PATH, self.FOLDER_PATH)

        os.makedirs(self.PLACEHOLDER_PATH)
        shutil.copy(self.STATIC_IMG_PATH, self.PLACEHOLDER_PATH)

    def test_wrong_token(self):
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object obj.path %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object %}'))
        self.assertRaises(TemplateSyntaxError, lambda: Template('{% load fb_versions %}{% version_object obj.path "medium" %}'))

    def test_hardcoded_path(self):
        t = Template('{% load fb_versions %}{% version_object path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "path": "_test/uploads/folder/testimage.jpg"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_obj_path(self):
        t = Template('{% load fb_versions %}{% version_object obj.path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_with_obj(self):
        t = Template('{% load fb_versions %}{% version_object obj "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_suffix_as_variable(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    def test_non_existing_path(self):
        # FIXME: templatetag version with non-existing path
        t = Template('{% load fb_versions %}{% version_object path "large" as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "path": "_test/uploads/folder/testimagexxx.jpg"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, ""))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, ""))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    @patch('filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER', True)
    def test_force_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    def test_no_force_with_existing_image(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_IMAGE, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/folder/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    @patch('filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER', True)
    def test_force_with_non_existing_image(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_MISSING, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))

    @patch('filebrowser.templatetags.fb_versions.SHOW_PLACEHOLDER', True)
    @patch('filebrowser.templatetags.fb_versions.FORCE_PLACEHOLDER', False)
    def test_no_force_with_non_existing_image(self):
        t = Template('{% load fb_versions %}{% version_object obj suffix as version_large %}{{ version_large.url }}')
        c = Context({"obj": self.F_MISSING, "suffix": "large"})
        r = t.render(c)
        self.assertEqual(c["version_large"].url, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))
        self.assertEqual(r, os.path.join(settings.MEDIA_URL, "_test/_versions/placeholders/testimage_large.jpg"))
