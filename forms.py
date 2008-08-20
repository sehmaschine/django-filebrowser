# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

import re, os

alnum_name_re = re.compile(r'^[a-zA-Z0-9_-]+$')


class MakeDirForm(forms.Form):
    
    def __init__(self, path_server, path, *args, **kwargs):
        self.PATH_SERVER = path_server
        self.path = path
        super(MakeDirForm, self).__init__(*args, **kwargs)
    
    dir_name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' },
                                max_length=50,
                                min_length=3)),
                                label=u'Directory',
                                help_text=_('The directory will automatically be converted to lowercase. Only letters, numbers, underscores and hyphens are allowed.'),
                                required=True)
                     
    def clean_dir_name(self):

        if self.cleaned_data['dir_name']:
            # only letters, numbers and underscores are allowed.
            if not alnum_name_re.search(self.cleaned_data['dir_name']):
                raise forms.ValidationError(_('Only letters, numbers, underscores and hyphens are allowed.'))
            # directory must not already exist.
            if os.path.isdir(os.path.join(self.PATH_SERVER, self.path, self.cleaned_data['dir_name'].lower())):
                raise forms.ValidationError(_('The directory already exists.'))
        
        return self.cleaned_data['dir_name']
        

