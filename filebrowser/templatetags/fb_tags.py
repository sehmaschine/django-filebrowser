# coding: utf-8

from django import template
from django.template import TemplateSyntaxError
from django.utils.http import urlquote
from django.utils.safestring import mark_safe

from filebrowser.settings import EXTENSIONS, SELECT_FORMATS


register = template.Library()


@register.inclusion_tag('filebrowser/include/_response.html', takes_context=True)
def query_string(context, add=None, remove=None):
    """
    Allows the addition and removal of query string parameters.

    _response.html is just {{ response }}

    Usage:
    http://www.url.com/{% query_string "param_to_add=value, param_to_add=value" "param_to_remove, params_to_remove" %}
    http://www.url.com/{% query_string "" "filter" %}filter={{new_filter}}
    http://www.url.com/{% query_string "sort=value" "sort" %}
    """

    # Written as an inclusion tag to simplify getting the context.
    add = string_to_dict(add)
    remove = string_to_list(remove)
    params = context['query'].copy()
    response = get_query_string(params, add, remove)
    return {'response': response}


def query_helper(query, add=None, remove=None):
    """
    Helper Function for use within views.
    """

    add = string_to_dict(add)
    remove = string_to_list(remove)
    params = query.copy()
    return get_query_string(params, add, remove)


def get_query_string(p, new_params=None, remove=None):
    """
    Add and remove query parameters. From `django.contrib.admin`.
    """

    if new_params is None:
        new_params = {}
    if remove is None:
        remove = []
    for r in remove:
        for k in list(p):
            if k == r:
                del p[k]
    for k, v in new_params.items():
        if k in p and v is None:
            del p[k]
        elif v is not None:
            p[k] = v
    return '?' + '&'.join([u'%s=%s' % (urlquote(k), urlquote(v)) for k, v in p.items()])


def string_to_dict(string):
    """
    Usage:
        {{ url|thumbnail:"width=10,height=20" }}
        {{ url|thumbnail:"width=10" }}
        {{ url|thumbnail:"height=20" }}
    """

    kwargs = {}
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '':
                continue
            kw, val = arg.split('=', 1)
            kwargs[kw] = val
    return kwargs


def string_to_list(string):
    """
    Usage:
        {{ url|thumbnail:"width,height" }}
    """

    args = []
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '':
                continue
            args.append(arg)
    return args


# class SelectableNode(template.Node):
#     def __init__(self, file_format, query_type):
#         self.file_format = template.Variable(file_format)
#         self.query_type = template.Variable(query_type)
#
#     def render(self, context):
#         try:
#             file_format = self.file_format.resolve(context)
#         except template.VariableDoesNotExist:
#             file_format = ''
#         try:
#             query_type = self.query_type.resolve(context)
#         except template.VariableDoesNotExist:
#             query_type = ''
#         selectable = True
#         if query_type:
#
#         if file_format and query_type and filetype in SELECT_FORMATS[format]:
#             selectable = True
#         elif filetype and format and filetype not in SELECT_FORMATS[format]:
#             selectable = False
#         else:
#             selectable = True
#         context['selectable'] = selectable
#         return ''
#
#
# def selectable(parser, token):
#
#     try:
#         tag, file_format, query_type = token.split_contents()
#     except:  # noqa
#         raise TemplateSyntaxError("%s tag requires 2 arguments" % token.contents.split()[0])
#
#     return SelectableNode(file_format, query_type)
#
# register.tag(selectable)


def get_file_extensions(qs):
    extensions = []
    if "type" in qs and qs.get("type") in SELECT_FORMATS:
        for format in SELECT_FORMATS.get(qs.get("type"), []):
            extensions.extend(EXTENSIONS[format])
    else:
        for k, v in EXTENSIONS.items():
            for item in v:
                if item:
                    extensions.append(item)
    return extensions


# Django 1.9 auto escapes simple_tag unless marked as safe
@register.simple_tag(name='get_file_extensions')
def get_file_extensions_safe(qs):
    return mark_safe(get_file_extensions(qs))
