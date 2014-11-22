# coding: utf-8

# DJANGO IMPORTS
from django.test import TestCase
from django.http import QueryDict

# FILEBROWSER IMPORTS
from filebrowser.templatetags.fb_tags import get_file_extensions


class TemplateTagsTests(TestCase):
    def test_get_file_extensions(self):
        self.assertEqual(sorted(get_file_extensions('')),
            sorted(['.pdf', '.doc', '.rtf', '.txt', '.xls', '.csv', '.docx', '.mov',
            '.wmv', '.mpeg', '.mpg', '.avi', '.rm', '.jpg', '.jpeg', '.gif', '.png',
            '.tif', '.tiff', '.mp3', '.mp4', '.wav', '.aiff', '.midi', '.m4p']))
        self.assertEqual(
            get_file_extensions(QueryDict('type=image')),
            ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff']
        )
