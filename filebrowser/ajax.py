# -*- coding: utf-8 -*-

import os

from django.shortcuts import HttpResponse

from filebrowser.fb_settings import MEDIA_ROOT, DIRECTORY

def checkfilename(request):
    """
    Check, if filename already exists in a directory.
    """
    
    directory = request.POST.get('dir')
    filename = request.POST.get('filename')
    
    if os.path.isfile(os.path.join(MEDIA_ROOT, DIRECTORY, directory, filename)):
        data = "exists"
    else:
        data = ""
    
    return HttpResponse(data)
    

