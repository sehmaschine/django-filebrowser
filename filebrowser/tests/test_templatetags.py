# coding: utf-8

# DJANGO IMPORTS
from django.test import TestCase

# FILEBROWSER IMPORTS
from filebrowser.templatetags.fb_tags import get_file_extensions_for_file_type


class TemplateTagsTests(TestCase):
    def test_get_file_extensions_for_file_type(self):
        self.assertEqual(get_file_extensions_for_file_type(''), [])
        self.assertEqual(
            get_file_extensions_for_file_type('image'),
            ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']
        )
