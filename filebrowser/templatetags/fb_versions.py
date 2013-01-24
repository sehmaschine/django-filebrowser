# coding: utf-8

# PYTHON IMPORTS
import os, re
from time import gmtime

# DJANGO IMPORTS
from django.template import Library, Node, Variable, VariableDoesNotExist, TemplateSyntaxError
from django.conf import settings
from django.utils.encoding import force_unicode, smart_str
from django.core.files import File


# FILEBROWSER IMPORTS
from filebrowser.settings import DIRECTORY, VERSIONS, PLACEHOLDER, SHOW_PLACEHOLDER, FORCE_PLACEHOLDER
from filebrowser.functions import get_version_path, version_generator
from filebrowser.base import FileObject
from filebrowser.sites import get_default_site
register = Library()


class VersionNode(Node):
    def __init__(self, src, version_prefix):
        self.src = Variable(src)
        if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")):
            self.version_prefix = version_prefix[1:-1]
        else:
            self.version_prefix = None
            self.version_prefix_var = Variable(version_prefix)
        
    def render(self, context):
        try:
            source = self.src.resolve(context)
        except VariableDoesNotExist:
            return None
        if self.version_prefix:
            version_prefix = self.version_prefix
        else:
            try:
                version_prefix = self.version_prefix_var.resolve(context)
            except VariableDoesNotExist:
                return None
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
            version_path = get_version_path(source, version_prefix, site=site)
            if not site.storage.isfile(version_path):
                version_path = version_generator(source, version_prefix, site=site)
            elif site.storage.modified_time(source) > site.storage.modified_time(version_path):
                version_path = version_generator(source, version_prefix, force=True, site=site)
            return site.storage.url(version_path)
        except:
            return ""


def version(parser, token):
    """
    Displaying a version of an existing Image according to the predefined VERSIONS settings (see filebrowser settings).
    {% version field_name.path version_prefix %}
    
    Use {% version my_image.path 'medium' %} in order to display the medium-size
    version of an Image stored in a field name my_image.
    
    version_prefix can be a string or a variable. if version_prefix is a string, use quotes.
    """
    
    try:
        tag, src, version_prefix = token.split_contents()
    except:
        raise TemplateSyntaxError, "%s tag requires 2 arguments" % token.contents.split()[0]
    if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")) and version_prefix.lower()[1:-1] not in VERSIONS:
        raise TemplateSyntaxError, "%s tag received bad version_prefix %s" % (tag, version_prefix)
    return VersionNode(src, version_prefix)


class VersionObjectNode(Node):
    def __init__(self, src, version_prefix, var_name):
        self.var_name = var_name
        self.src = Variable(src)
        if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")):
            self.version_prefix = version_prefix[1:-1]
        else:
            self.version_prefix = None
            self.version_prefix_var = Variable(version_prefix)
    
    def render(self, context):
        try:
            source = self.src.resolve(context)
        except VariableDoesNotExist:
            return None
        if self.version_prefix:
            version_prefix = self.version_prefix
        else:
            try:
                version_prefix = self.version_prefix_var.resolve(context)
            except VariableDoesNotExist:
                return None
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
            version_path = get_version_path(source, version_prefix, site=site)
            if not site.storage.isfile(version_path):
                version_path = version_generator(source, version_prefix, site=site)
            elif site.storage.modified_time(source) > site.storage.modified_time(version_path):
                version_path = version_generator(source, version_prefix, force=True, site=site)
            context[self.var_name] = FileObject(version_path, site=site)
        except Exception as e:
            if settings.TEMPLATE_DEBUG:
                raise e
            context[self.var_name] = ""
        return ''


def version_object(parser, token):
    """
    Returns a context variable 'version_object'.
    {% version_object field_name.path version_prefix %}
    
    Use {% version_object my_image.path 'medium' %} in order to retrieve the medium
    version of an Image stored in a field name my_image.
    Use {% version_object my_image.path 'medium' as var %} in order to use 'var' as
    your context variable.
    
    version_prefix can be a string or a variable. if version_prefix is a string, use quotes.
    """
    
    try:
        #tag, src, version_prefix = token.split_contents()
        tag, arg = token.contents.split(None, 1)
    except:
        raise TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) (.*?) as (\w+)', arg)
    if not m:
        raise TemplateSyntaxError, "%r tag had invalid arguments" % tag
    src, version_prefix, var_name = m.groups()
    if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")) and version_prefix.lower()[1:-1] not in VERSIONS:
        raise TemplateSyntaxError, "%s tag received bad version_prefix %s" % (tag, version_prefix)
    return VersionObjectNode(src, version_prefix, var_name)


class VersionSettingNode(Node):
    def __init__(self, version_prefix):
        if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")):
            self.version_prefix = version_prefix[1:-1]
        else:
            self.version_prefix = None
            self.version_prefix_var = Variable(version_prefix)
    
    def render(self, context):
        if self.version_prefix:
            version_prefix = self.version_prefix
        else:
            try:
                version_prefix = self.version_prefix_var.resolve(context)
            except VariableDoesNotExist:
                return None
        context['version_setting'] = VERSIONS[version_prefix]
        return ''


def version_setting(parser, token):
    """
    Get Information about a version setting.
    """
    
    try:
        tag, version_prefix = token.split_contents()
    except:
        raise TemplateSyntaxError, "%s tag requires 1 argument" % token.contents.split()[0]
    if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")) and version_prefix.lower()[1:-1] not in VERSIONS:
        raise TemplateSyntaxError, "%s tag received bad version_prefix %s" % (tag, version_prefix)
    return VersionSettingNode(version_prefix)


register.tag(version)
register.tag(version_object)
register.tag(version_setting)

