# coding: utf-8

# imports
import re, os

# django imports
from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext as _

# filebrowser imports
from filebrowser.settings import MAX_UPLOAD_SIZE, FOLDER_REGEX
from filebrowser.functions import convert_filename

alnum_name_re = re.compile(FOLDER_REGEX, re.U)

# CHOICES
TRANSPOSE_CHOICES = (
    ("", u"-----"),
    ("0", _(u"Flip horizontal")),
    ("1", _(u"Flip vertical")),
    ("2", _(u"Rotate 90° CW")),
    ("4", _(u"Rotate 90° CCW")),
    ("3", _(u"Rotate 180°")),
)


class CreateDirForm(forms.Form):
    """
    Form for creating a folder.
    """
    
    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(CreateDirForm, self).__init__(*args, **kwargs)
        
    name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'Name'), help_text=_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)
    
    def clean_dir_name(self):
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            # Folder must not already exist.
            if os.path.isdir(os.path.join(self.path, convert_filename(self.cleaned_data['name']))):
                raise forms.ValidationError(_(u'The Folder already exists.'))
        return convert_filename(self.cleaned_data['name'])


class ChangeForm(forms.Form):
    """
    Form for renaming a file/folder.
    """
    
    def __init__(self, *args, **kwargs):
        self.path = kwargs.pop("path", None)
        self.fileobject = kwargs.pop("fileobject", None)
        super(ChangeForm, self).__init__(*args, **kwargs)
    
    name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'Name'), help_text=_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)
    transpose = forms.ChoiceField(choices=TRANSPOSE_CHOICES, label=_(u'Flip/Rotate'), required=False)
    
    def clean_name(self):
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            #  folder/file must not already exist.
            if os.path.isdir(os.path.join(self.path, convert_filename(self.cleaned_data['name']))) and os.path.join(self.path, convert_filename(self.cleaned_data['name'])) != self.fileobject.path:
                raise forms.ValidationError(_(u'The Folder already exists.'))
            elif os.path.isfile(os.path.join(self.path, convert_filename(self.cleaned_data['name'])))  and os.path.join(self.path, convert_filename(self.cleaned_data['name'])) != self.fileobject.path:
                raise forms.ValidationError(_(u'The File already exists.'))
        return convert_filename(self.cleaned_data['name'])


