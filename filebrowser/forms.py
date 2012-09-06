# coding: utf-8

# PYTHON IMPORTS
import re, os

# DJANGO IMPORTS
from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _

# FILEBROWSER IMPORTS
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
        self.site = kwargs.pop("filebrowser_site", None)
        super(CreateDirForm, self).__init__(*args, **kwargs)
        
    name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'Name'), help_text=_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)
    
    def clean_name(self):
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            # Folder must not already exist.
            if self.site.storage.isdir(os.path.join(self.path, convert_filename(self.cleaned_data['name']))):
                raise forms.ValidationError(_(u'The Folder already exists.'))
        return convert_filename(self.cleaned_data['name'])


class ChangeForm(forms.Form):
    """
    Form for renaming a file/folder.
    """
    
    custom_action = forms.ChoiceField(label=_(u'Actions'), required=False)
    name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=_(u'Name'), help_text=_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'), required=True)
    
    def __init__(self, *args, **kwargs):
        self.path = kwargs.pop("path", None)
        self.fileobject = kwargs.pop("fileobject", None)
        from filebrowser.sites import site
        self.site = kwargs.pop("filebrowser_site", None)
        super(ChangeForm, self).__init__(*args, **kwargs)
        
        # Initialize choices of custom actions 
        choices = [("",u"-----"),]
        
        for name, action in self.site.applicable_actions(self.fileobject):
            choices.append((name, action.short_description))
        
        self.fields['custom_action'].choices=choices

    def clean_name(self):
        if self.cleaned_data['name']:
            # only letters, numbers, underscores, spaces and hyphens are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_(u'Only letters, numbers, underscores, spaces and hyphens are allowed.'))
            #  folder/file must not already exist.
            if self.site.storage.isdir(os.path.join(self.path, convert_filename(self.cleaned_data['name']))) and os.path.join(self.path, convert_filename(self.cleaned_data['name'])) != self.fileobject.path:
                raise forms.ValidationError(_(u'The Folder already exists.'))
            elif self.site.storage.isfile(os.path.join(self.path, convert_filename(self.cleaned_data['name'])))  and os.path.join(self.path, convert_filename(self.cleaned_data['name'])) != self.fileobject.path:
                raise forms.ValidationError(_(u'The File already exists.'))
        return convert_filename(self.cleaned_data['name'])


