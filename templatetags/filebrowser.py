# -*- coding: UTF-8 -*-
import os
import re

from django import template
from django.conf import settings
from django.db import models

# can't import directly from filebrowser,
# because the current file is also called filebrowser and has larger priority
filebrowser = models.get_app("filebrowser")
ImageModification = filebrowser.ImageModification
PATH_SERVER = filebrowser.PATH_SERVER

register = template.Library()


### FILTERS ### 

def modified_path(rel_orig_path, sysname):
    """ 
    Returns the relative filebrowser path to the modified image.
    If the modified image does not exist, it will be created
    
    Usage:
        {{ <path>|modified_path:<modification_sysname> }}
    
    Example:
        {{ "test/original.png"|modified_path:"gallery_default" }}
        
    """
    
    orig_path_server = os.path.join(PATH_SERVER, *rel_orig_path.split("/"))
    try:
        mod = ImageModification.objects.get(sysname=sysname)
    except:
        raise template.TemplateSyntaxError, "Image Modification with the sysname '%s' doesn't exist" % sysname
    
    mod_path = mod.modified_path(rel_orig_path)
    mod_path_server = os.path.join(PATH_SERVER, *mod_path.split("/"))
    
    # modified_path should also work for files in another server
    if os.path.isfile(orig_path_server):
        if not os.path.isfile(mod_path_server):
            try:
                mod.process_image(orig_path_server)
            except:
                pass
    return mod_path

register.filter('modified_path', modified_path)

