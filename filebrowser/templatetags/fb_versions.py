# coding: utf-8

# PYTHON IMPORTS
import os, re
from time import gmtime

# DJANGO IMPORTS
from django.template import Library, Node, VariableDoesNotExist, TemplateSyntaxError
from django.conf import settings
from django.utils.encoding import force_unicode, smart_str
from django.core.files import File


# FILEBROWSER IMPORTS
from filebrowser.settings import VERSIONS, PLACEHOLDER, SHOW_PLACEHOLDER, FORCE_PLACEHOLDER
from filebrowser.functions import get_version_path, version_generator
from filebrowser.base import FileObject
from filebrowser.sites import get_default_site
register = Library()


class VersionNode(Node):
    def __init__(self, src, version_suffix):
        self.src = src
        self.version_suffix = version_suffix
        
    def render(self, context):
        try:
            source = self.src.resolve(context)
            version_suffix = self.version_suffix.resolve(context)
        except VariableDoesNotExist:
            return ''
        site = context.get('filebrowser_site', get_default_site())
        directory = site.directory
        try:
            if isinstance(source, FileObject):
                site = source.site
                source = source.path
            if isinstance(source, File):
                source = source.name
            source = force_unicode(source)
            if FORCE_PLACEHOLDER:
                source = PLACEHOLDER
            elif SHOW_PLACEHOLDER and not site.storage.isfile(source):
                source = PLACEHOLDER
            version_path = get_version_path(source, version_suffix, site=site)
            if not site.storage.isfile(version_path):
                version_path = version_generator(source, version_suffix, site=site)
            elif site.storage.modified_time(source) > site.storage.modified_time(version_path):
                version_path = version_generator(source, version_suffix, force=True, site=site)
            return site.storage.url(version_path)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
        return ''


def version(parser, token):
    """
    Displaying a version of an existing Image according to the predefined VERSIONS settings (see filebrowser settings).
    {% version field_name.path version_suffix %}
    
    Use {% version my_image.path 'medium' %} in order to display the medium-size
    version of an Image stored in a field name my_image.
    
    version_suffix can be a string or a variable. if version_suffix is a string, use quotes.
    """
    bits = token.split_contents()
    tag_name = bits[0]

    if len(bits) < 3:
        raise TemplateSyntaxError("%s tag requires 2 arguments" % tag_name)

    src = parser.compile_filter(bits[1])
    version_suffix = parser.compile_filter(bits[2])
    return VersionNode(src, version_suffix)


class VersionObjectNode(Node):
    def __init__(self, src, version_suffix, var_name):
        self.var_name = var_name
        self.src = src
        self.version_suffix = version_suffix
    
    def render(self, context):
        try:
            source = self.src.resolve(context)
            version_suffix = self.version_suffix.resolve(context)
        except VariableDoesNotExist:
            return ''
        site = context.get('filebrowser_site', get_default_site())
        directory = site.directory
        try:
            if isinstance(source, FileObject):
                site = source.site
                source = source.path
            if isinstance(source, File):
                source = source.name
            source = force_unicode(source)
            if FORCE_PLACEHOLDER:
                source = PLACEHOLDER
            elif SHOW_PLACEHOLDER and not site.storage.isfile(source):
                source = PLACEHOLDER
            version_path = get_version_path(source, version_suffix, site=site)
            if not site.storage.isfile(version_path):
                version_path = version_generator(source, version_suffix, site=site)
            elif site.storage.modified_time(source) > site.storage.modified_time(version_path):
                version_path = version_generator(source, version_suffix, force=True, site=site)
            context[self.var_name] = FileObject(version_path, site=site)
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            context[self.var_name] = ''
        return ''


def version_object(parser, token):
    """
    Returns a context variable 'version_object'.
    {% version_object field_name.path version_suffix %}
    
    Use {% version_object my_image.path 'medium' %} in order to retrieve the medium
    version of an Image stored in a field name my_image.
    Use {% version_object my_image.path 'medium' as var %} in order to use 'var' as
    your context variable.
    
    version_suffix can be a string or a variable. if version_suffix is a string, use quotes.
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != 5:
        raise TemplateSyntaxError("%s tag requires 4 arguments" % tag_name)
    if bits[-2] != 'as':
        raise TemplateSyntaxError("%s tag's third argument must be 'as'" % tag_name)
    src = parser.compile_filter(bits[1])
    version_suffix = parser.compile_filter(bits[2])
    var_name = bits[4]
    return VersionObjectNode(src, version_suffix, var_name)


class VersionSettingNode(Node):
    def __init__(self, version_suffix):
        self.version_suffix = version_suffix
    
    def render(self, context):
        try:
            version_suffix = self.version_suffix.resolve(context)
        except VariableDoesNotExist:
            return ''
        context['version_setting'] = VERSIONS[version_suffix]
        return ''


def version_setting(parser, token):
    """
    Get Information about a version setting.
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != 2:
        raise TemplateSyntaxError("%s tag requires 1 argument" % tag_name)
    version_suffix = parser.compile_filter(bits[1])
    return VersionSettingNode(version_suffix)


register.tag(version)
register.tag(version_object)
register.tag(version_setting)

