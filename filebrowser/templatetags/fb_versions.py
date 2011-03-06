# coding: utf-8

# imports
import os, re
from time import gmtime

# django imports
from django.template import Library, Node, Variable, VariableDoesNotExist, TemplateSyntaxError
from django.conf import settings
from django.utils.encoding import force_unicode, smart_str

# filebrowser imports
from filebrowser.settings import MEDIA_ROOT, MEDIA_URL, VERSIONS
from filebrowser.functions import url_to_path, path_to_url, get_version_path, version_generator
from filebrowser.base import FileObject

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
        try:
            source = force_unicode(source)
            version_path = get_version_path(url_to_path(source), version_prefix)
            if not os.path.isfile(smart_str(os.path.join(MEDIA_ROOT, version_path))):
                # create version
                version_path = version_generator(url_to_path(source), version_prefix)
            elif os.path.getmtime(smart_str(os.path.join(MEDIA_ROOT, url_to_path(source)))) > os.path.getmtime(smart_str(os.path.join(MEDIA_ROOT, version_path))):
                # recreate version if original image was updated
                version_path = version_generator(url_to_path(source), version_prefix, force=True)
            return path_to_url(version_path)
        except:
            return ""


def version(parser, token):
    """
    Displaying a version of an existing Image according to the predefined VERSIONS settings (see filebrowser settings).
    {% version field_name version_prefix %}
    
    Use {% version my_image 'medium' %} in order to display the medium-size
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
        try:
            source = force_unicode(source)
            version_path = get_version_path(url_to_path(source), version_prefix)
            if not os.path.isfile(smart_str(os.path.join(MEDIA_ROOT, version_path))):
                # create version
                version_path = version_generator(url_to_path(source), version_prefix)
            elif os.path.getmtime(smart_str(os.path.join(MEDIA_ROOT, url_to_path(source)))) > os.path.getmtime(smart_str(os.path.join(MEDIA_ROOT, version_path))):
                # recreate version if original image was updated
                version_path = version_generator(url_to_path(source), version_prefix, force=True)
            context[self.var_name] = FileObject(version_path)
        except:
            context[self.var_name] = ""
        return ''


def version_object(parser, token):
    """
    Returns a context variable 'version_object'.
    {% version_object field_name version_prefix %}
    
    Use {% version_object my_image 'medium' %} in order to retrieve the medium
    version of an Image stored in a field name my_image.
    Use {% version_object my_image 'medium' as var %} in order to use 'var' as
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


