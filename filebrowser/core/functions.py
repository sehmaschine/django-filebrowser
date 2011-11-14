# coding: utf-8

# imports
import os
from time import gmtime, strftime, localtime, mktime, time
from tempfile import NamedTemporaryFile

# django imports
from django.utils.translation import ugettext as _
from django.core.files import File
from django.utils.encoding import smart_unicode

# filebrowser imports
from filebrowser.core.settings import *

# PIL import
if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


def path_strip(path, root):
    if not path or not root:
        return path
    path = os.path.normcase(path)
    root = os.path.normcase(root)
    if path.startswith(root):
        return path[len(root):]
    return path

def url_strip(url, root):
    if not url or not root:
        return url
    if url.startswith(root):
        return url[len(root):]
    return url


def sort_by_attr(seq, attr):
    """
    Sort the sequence of objects by object's attribute
    
    Arguments:
    seq  - the list or any sequence (including immutable one) of objects to sort.
    attr - the name of attribute to sort by
    
    Returns:
    the sorted list of objects.
    """
    import operator
    
    # Use the "Schwartzian transform"
    # Create the auxiliary list of tuples where every i-th tuple has form
    # (seq[i].attr, i, seq[i]) and sort it. The second item of tuple is needed not
    # only to provide stable sorting, but mainly to eliminate comparison of objects
    # (which can be expensive or prohibited) in case of equal attribute values.
    intermed = map(None, map(getattr, seq, (attr,)*len(seq)), xrange(len(seq)), seq)
    intermed.sort()
    return map(operator.getitem, intermed, (-1,) * len(intermed))


def url_join(*args):
    """
    URL join routine.
    """
    
    if args[0].startswith("http://"):
        url = "http://"
    else:
        url = "/"
    for arg in args:
        arg = arg.replace("\\", "/")
        arg_split = arg.split("/")
        for elem in arg_split:
            if elem != "" and elem != "http:":
                url = url + elem + "/"
    # remove trailing slash for filenames
    if os.path.splitext(args[-1])[1]:
        url = url.rstrip("/")
    return url


def get_path(path, site=None):
    """
    Get path.
    """
    if path.startswith('.') or os.path.isabs(path) or not site.storage.isdir(os.path.join(site.directory, path)):
        return None
    return path


def get_file(path, filename, site=None):
    """
    Get file (or folder).
    """
    converted_path = smart_unicode(os.path.join(site.directory, path, filename))
    if not site.storage.isfile(converted_path) and not site.storage.isdir(converted_path):
        return None
    return filename


def get_file_type(filename):
    """
    Get file type as defined in EXTENSIONS.
    """
    
    file_extension = os.path.splitext(filename)[1].lower()
    file_type = ''
    for k,v in EXTENSIONS.iteritems():
        for extension in v:
            if file_extension == extension.lower():
                file_type = k
    return file_type


def get_breadcrumbs(query, path):
    """
    Get breadcrumbs.
    """
    
    breadcrumbs = []
    dir_query = ""
    if path:
        for item in path.split(os.sep):
            dir_query = os.path.join(dir_query,item)
            breadcrumbs.append([item,dir_query])
    return breadcrumbs


def get_filterdate(filterDate, dateTime):
    """
    Get filterdate.
    """
    
    returnvalue = ''
    dateYear = strftime("%Y", gmtime(dateTime))
    dateMonth = strftime("%m", gmtime(dateTime))
    dateDay = strftime("%d", gmtime(dateTime))
    if filterDate == 'today' and int(dateYear) == int(localtime()[0]) and int(dateMonth) == int(localtime()[1]) and int(dateDay) == int(localtime()[2]): returnvalue = 'true'
    elif filterDate == 'thismonth' and dateTime >= time()-2592000: returnvalue = 'true'
    elif filterDate == 'thisyear' and int(dateYear) == int(localtime()[0]): returnvalue = 'true'
    elif filterDate == 'past7days' and dateTime >= time()-604800: returnvalue = 'true'
    elif filterDate == '': returnvalue = 'true'
    return returnvalue


def handle_file_upload(path, file, site):
    """
    Handle File Upload.
    """
    
    uploadedfile = None
    try:
        file_path = os.path.join(path, file.name)
        uploadedfile = site.storage.save(file_path, file)
    except Exception, inst:
        raise inst
    return uploadedfile


def is_selectable(filename, selecttype):
    """
    Get select type as defined in FORMATS.
    """
    
    file_extension = os.path.splitext(filename)[1].lower()
    select_types = []
    for k,v in SELECT_FORMATS.iteritems():
        for extension in v:
            if file_extension == extension.lower():
                select_types.append(k)
    return select_types


def convert_filename(value):
    """
    Convert Filename.
    """
    
    if CONVERT_FILENAME:
        return value.replace(" ", "_").lower()
    else:
        return value


