# coding: utf-8

from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext as _
import re, os

# get settings
from filebrowser.fb_settings import *
# get functions
from filebrowser.functions import _get_file_type

alnum_name_re = re.compile(r'^[\sa-zA-Z0-9._/-]+$')


class MakeDirForm(forms.Form):
    
    def __init__(self, path_server, path, *args, **kwargs):
        self.PATH_SERVER = path_server
        self.path = path
        super(MakeDirForm, self).__init__(*args, **kwargs)
    
    dir_name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'Name'), help_text=_(u'The Name will automatically be converted to lowercase. Only letters, numbers, underscores and hyphens are allowed.'), required=True)
                     
    def clean_dir_name(self):
        
        if self.cleaned_data['dir_name']:
            # only letters, numbers and underscores are allowed.
            if not alnum_name_re.search(self.cleaned_data['dir_name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores and hyphens are allowed.'))
            # directory must not already exist.
            if os.path.isdir(os.path.join(self.PATH_SERVER, self.path, self.cleaned_data['dir_name'].lower())):
                raise forms.ValidationError(_(u'The Folder already exists.'))
            # check banned folder names
            if self.cleaned_data['dir_name'] in DISALLOWED_FOLDER_NAMES:
                raise forms.ValidationError(_(u'Disallowed Folder Name.'))
        
        return self.cleaned_data['dir_name']
    

class RenameForm(forms.Form):

    def __init__(self, path_server, path, file_extension, *args, **kwargs):
        self.PATH_SERVER = path_server
        self.path = path
        self.file_extension = file_extension
        super(RenameForm, self).__init__(*args, **kwargs)
    
    name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'New Name'), help_text=_('The Name will automatically be converted to lowercase. Only letters, numbers, underscores and hyphens are allowed.'), required=True)
    
    def clean_name(self):
    
        if self.cleaned_data['name']:
            # only letters, numbers and underscores are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores and hyphens are allowed.'))
            # file/directory must not already exist.
            if os.path.isdir(os.path.join(self.PATH_SERVER, self.path, self.cleaned_data['name'].lower())) or os.path.isfile(os.path.join(self.PATH_SERVER, self.path, self.cleaned_data['name'].lower() + self.file_extension)):
                raise forms.ValidationError(_(u'The File/Folder already exists.'))
        
        return self.cleaned_data['name']
    

class BaseUploadFormSet(BaseFormSet):

    # this is just for passing the parameters (path_server, path) to the uploadform.
    # overly complicated, but necessary for the clean-methods in UploadForm.
    # DO NOT CHANGE ANYTHING HERE.
    # if you need to make modifications to the uploadform - use UploadForm below.
    
    def __init__(self, **kwargs):
        self.path_server = kwargs['path_server']
        self.path = kwargs['path']
        del kwargs['path_server']
        del kwargs['path']
        super(BaseUploadFormSet, self).__init__(**kwargs)
    
    def _construct_form(self, i, **kwargs):
        # this works because BaseFormSet._construct_form() passes **kwargs
        # to the form's __init__()
        kwargs["path_server"] = self.path_server
        kwargs["path"] = self.path
        return super(BaseUploadFormSet, self)._construct_form(i, **kwargs)
    

class UploadForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.path_server = kwargs['path_server']
        self.path = kwargs['path']
        del kwargs['path_server']
        del kwargs['path']
        super(UploadForm, self).__init__(*args, **kwargs)
    
    file = forms.FileField(label=_(u'File'))
    use_image_generator = forms.BooleanField(label=_(u'Use Image Generator'), required=False)
    
    def clean_file(self):
        if self.cleaned_data['file']:
            filename = self.cleaned_data['file'].name
            
            # CHECK IF FILE EXISTS
            dir_list = os.listdir(os.path.join(self.path_server, self.path))
            if filename in dir_list:
                raise forms.ValidationError(_(u'File already exists.'))
                
            # TODO: CHECK IF VERSIONS_PATH EXISTS (IF USE_IMAGE_GENERATOR IS TRUE)
            
            # CHECK FILENAME
            if not alnum_name_re.search(filename):
                raise forms.ValidationError(_(u'Filename is not allowed.'))
                
            # CHECK EXTENSION / FILE_TYPE
            file_type = _get_file_type(filename)
            if not file_type:
                raise forms.ValidationError(_(u'File extension is not allowed.'))
                
            # CHECK FILESIZE
            filesize = self.cleaned_data['file'].size
            if filesize > MAX_UPLOAD_SIZE:
                raise forms.ValidationError(_(u'Filesize exceeds allowed Upload Size.'))
                
            self.cleaned_data['file'].name = self.cleaned_data['file'].name.replace(' ', '_')
        return self.cleaned_data['file']
        

