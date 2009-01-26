# coding: utf-8

from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext as _
import re, os

# get settings
from filebrowser.fb_settings import *
# get functions
from filebrowser.functions import _get_file_type
from filebrowser.models import File, ImageModification

alnum_name_re = re.compile(r'^[a-zA-Z0-9._/\- ]+$')


class MakeDirForm(forms.Form):
    
    def __init__(self, path_server, path, *args, **kwargs):
        self.PATH_SERVER = path_server
        self.path = path
        super(MakeDirForm, self).__init__(*args, **kwargs)
    
    dir_name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=u'Directory', help_text=_('The directory will automatically be converted to lowercase. Only letters, numbers, underscores and hyphens are allowed.'), required=True)
                     
    def clean_dir_name(self):
        
        if self.cleaned_data['dir_name']:
            # only letters, numbers and underscores are allowed.
            if not alnum_name_re.search(self.cleaned_data['dir_name']):
                raise forms.ValidationError(_('Only letters, numbers, underscores and hyphens are allowed.'))
            # directory must not already exist.
            if os.path.isdir(os.path.join(self.PATH_SERVER, self.path, self.cleaned_data['dir_name'].lower())):
                raise forms.ValidationError(_('The directory already exists.'))
        
        return self.cleaned_data['dir_name']
    
class ChangeForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs = {
                'class': 'vTextField',
                'max_length': 50,
                'min_length': 3,
                },
            ),
        label=_('File Name'),
        required=True,
        )
    
    def __init__(self, *args, **kwargs):
        super(ChangeForm, self).__init__(*args, **kwargs)
        if self.instance.file_type == "Image": 
            self.fields['image_modifications'] = forms.ModelMultipleChoiceField(
                label=_("Modifications to apply to images"),
                queryset=ImageModification.objects.all(),
                required=False,
                )
        self.fields['title'].widget.attrs['class'] = 'vTextField'
        self.fields['description'].widget.attrs['class'] = 'vLargeTextField'
    
    class Meta:
        model = File
        exclude = ['path', 'width', 'height', 'size', 'file_type']
        
    def clean_name(self):
        file_obj = self.instance
        if self.cleaned_data['name'] != self.instance.get_filename_base():
            # only letters, numbers and underscores are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_('Only letters, numbers, underscores and hyphens are allowed.'))
            # file/directory must not already exist.
            if os.path.isdir(os.path.join(file_obj.get_abs_dir(), self.cleaned_data['name'].lower())) or os.path.isfile(os.path.join(file_obj.get_abs_dir(), self.cleaned_data['name'].lower() + file_obj.get_filename_ext())):
                raise forms.ValidationError(_('The file/directory already exists.'))
        return self.cleaned_data['name']

class RenameForm(forms.Form):

    def __init__(self, path_server, path, file_extension, *args, **kwargs):
        self.PATH_SERVER = path_server
        self.path = path
        self.file_extension = file_extension
        super(RenameForm, self).__init__(*args, **kwargs)
    
    name = forms.CharField(widget=forms.TextInput(attrs=dict({ 'class': 'vTextField' }, max_length=50, min_length=3)), label=u'Name', help_text=_('The name will automatically be converted to lowercase. Only letters, numbers, underscores and hyphens are allowed.'), required=True)
    
    def clean_name(self):
    
        if self.cleaned_data['name']:
            # only letters, numbers and underscores are allowed.
            if not alnum_name_re.search(self.cleaned_data['name']):
                raise forms.ValidationError(_('Only letters, numbers, underscores and hyphens are allowed.'))
            # file/directory must not already exist.
            if os.path.isdir(os.path.join(self.PATH_SERVER, self.path, self.cleaned_data['name'].lower())) or os.path.isfile(os.path.join(self.PATH_SERVER, self.path, self.cleaned_data['name'].lower() + self.file_extension)):
                raise forms.ValidationError(_('The file/directory already exists.'))
        
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

class UploadSettingsForm(forms.Form):
    rename_to_timestamp = forms.BooleanField(
        label=_("Rename files to upload timestamp"),
        initial=False,
        widget=forms.CheckboxInput(attrs={'class':'vCheckboxField'}),
        required = False,
        )
    convert_to_lower_case = forms.BooleanField(
        label=_("Convert file names to lower case"),
        initial=True,
        widget=forms.CheckboxInput(attrs={'class':'vCheckboxField'}),
        required = False,
        )
    change_spaces_to_underscores = forms.BooleanField(
        label=_("Change spaces to underscores in the file names"),
        initial=True,
        widget=forms.CheckboxInput(attrs={'class':'vCheckboxField'}),
        required = False,
        )
    overwrite_existing = forms.BooleanField(
        label=_("Overwrite existing files with the same names"),
        initial=False,
        widget=forms.CheckboxInput(attrs={'class':'vCheckboxField'}),
        required = False,
        )
    extract_archives = forms.BooleanField(
        label=_("Extract ZIP archives"),
        initial=False,
        widget=forms.CheckboxInput(attrs={'class':'vCheckboxField'}),
        required = False,
        )
    image_modifications = forms.ModelMultipleChoiceField(
        label=_("Modifications to apply to images"),
        queryset=ImageModification.objects.all(),
        required=False,
        )
    
class UploadForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.path_server = kwargs['path_server']
        self.path = kwargs['path']
        del kwargs['path_server']
        del kwargs['path']
        super(UploadForm, self).__init__(*args, **kwargs)
    
    file = forms.FileField(
        label=_("File"),
        )
    title = forms.CharField(
        required=False,
        label=_("Title"),
        )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label=_("Description"),
        )
    use_image_generator = forms.BooleanField(label=_("Use Image Generator"), help_text=_('Use Image Generator.'), required=False)
    
    def clean_file(self):
        if self.cleaned_data['file']:
            filename = self.cleaned_data['file'].name
            
            # TODO: CHECK IF VERSIONS_PATH EXISTS (IF USE_IMAGE_GENERATOR IS TRUE)
            
            # CHECK FILENAME
            if not alnum_name_re.search(filename):
                raise forms.ValidationError(_('Filename is not allowed.'))
                
            # CHECK EXTENSION / FILE_TYPE
            file_type = _get_file_type(filename)
            if not file_type:
                raise forms.ValidationError(_('File extension is not allowed.'))
                
            # CHECK FILESIZE
            filesize = self.cleaned_data['file'].size
            if filesize > MAX_UPLOAD_SIZE:
                raise forms.ValidationError(_('Filesize exceeds allowed Upload Size.'))
        return self.cleaned_data['file']
        

