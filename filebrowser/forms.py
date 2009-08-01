# coding: utf-8

import re, os

from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext as _

# filebrowser imports
from filebrowser.fb_settings import MAX_UPLOAD_SIZE
from filebrowser.functions import _get_file_type, _convert_filename

alnum_name_re = re.compile(r'^[\sa-zA-Z0-9._/-]+$')

class MakeDirForm(forms.Form):
    """
    Form for creating Directory.
    """
    
    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(MakeDirForm, self).__init__(*args, **kwargs)
        
    dir_name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'Name'), help_text=_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)
    
    def clean_dir_name(self):   
        if self.cleaned_data['dir_name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['dir_name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            # directory must not already exist.
            if os.path.isdir(os.path.join(self.path, _convert_filename(self.cleaned_data['dir_name']))):
                raise forms.ValidationError(_(u'The Folder already exists.'))
        return _convert_filename(self.cleaned_data['dir_name'])
    

class RenameForm(forms.Form):
    """
    Form for renaming File/Directory.
    """
    
    def __init__(self, path, file_extension, *args, **kwargs):
        self.path = path
        self.file_extension = file_extension
        super(RenameForm, self).__init__(*args, **kwargs)
    
    name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'New Name'), help_text=_('Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)
    
    def clean_name(self):
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            # file/directory must not already exist.
            if os.path.isdir(os.path.join(self.path, _convert_filename(self.cleaned_data['name']))) or os.path.isfile(os.path.join(self.path, _convert_filename(self.cleaned_data['name']) + self.file_extension)):
                raise forms.ValidationError(_(u'The File/Folder already exists.'))
        return _convert_filename(self.cleaned_data['name'])
    

