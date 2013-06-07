# coding: utf-8

# DJANGO IMPORTS
from django.template import Library
from django.conf import settings
from django.utils.encoding import force_unicode
from django.core.files import File


# FILEBROWSER IMPORTS
from filebrowser.settings import VERSIONS, PLACEHOLDER, SHOW_PLACEHOLDER, FORCE_PLACEHOLDER
from filebrowser.functions import get_version_path, version_generator
from filebrowser.base import FileObject
from filebrowser.sites import get_default_site
register = Library()


def _get_version_path(context, source, version_suffix):
    if version_suffix not in VERSIONS:
        return None, ''
    site = context.get('filebrowser_site', get_default_site())
    if isinstance(source, FileObject):
        site = source.site
        source = source.path
    if isinstance(source, File):
        source = source.name
    try:
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
    except:
        if settings.TEMPLATE_DEBUG:
            raise
        return None, ''

    return site, version_path


@register.simple_tag(takes_context=True)
def version(context, source, version_suffix):
    """
    Displaying a version of an existing Image according to the predefined VERSIONS settings (see filebrowser settings).
    {% version field_name.path version_suffix %}

    Use {% version my_image.path 'medium' %} in order to display the medium-size
    version of an Image stored in a field name my_image.

    version_suffix can be a string or a variable. if version_suffix is a string, use quotes.
    """
    site, version_path = _get_version_path(context, source, version_suffix)
    if not site or not version_path:
        return ''
    return site.storage.url(version_path)


@register.assignment_tag(takes_context=True)
def version_object(context, source, version_suffix):
    """
    Returns a context variable 'version_object'.
    {% version_object field_name.path version_suffix %}

    Use {% version_object my_image.path 'medium' as var %} in order to retrieve the medium
    version of an Image stored in a field name my_image and store it in the context as 'var'.

    version_suffix can be a string or a variable. if version_suffix is a string, use quotes.
    """
    site, version_path = _get_version_path(context, source, version_suffix)
    if not site or not version_path:
        return ''
    return FileObject(version_path, site=site)


@register.simple_tag(takes_context=True)
def version_setting(context, version_suffix):
    """
    Get Information about a version setting.
    """
    context['version_setting'] = VERSIONS.get(version_suffix, '')
    return ''
