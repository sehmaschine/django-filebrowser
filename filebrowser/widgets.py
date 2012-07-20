# coding: utf-8

# DJANGO IMPORTS
from django.template.loader import render_to_string
from django.forms.widgets import FileInput as DjangoFileInput
from django.forms.widgets import ClearableFileInput as DjangoClearableFileInput
from django.forms.widgets import CheckboxInput
from django.forms.fields import FilePathField
from django.utils.translation import ugettext, ugettext_lazy
from django.utils.safestring import mark_safe

# FILEBROWSER IMPORTS
from filebrowser.base import FileObject
from filebrowser.settings import ADMIN_THUMBNAIL


class FileInput(DjangoClearableFileInput):

    initial_text = ugettext_lazy('Currently')
    input_text = ugettext_lazy('Change')
    clear_checkbox_label = ugettext_lazy('Clear')
    template_with_initial = u'%(input)s %(preview)s'
    
    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'preview': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions['input'] = super(DjangoClearableFileInput, self).render(name, value, attrs)
        
        if value and hasattr(value, "url"):
            template = self.template_with_initial
            preview_template = render_to_string('filebrowser/widgets/fileinput.html', {
                'value': FileObject(value.name),
                'ADMIN_THUMBNAIL': ADMIN_THUMBNAIL,
            })
            substitutions["preview"] = preview_template
        
        return mark_safe(template % substitutions)


class ClearableFileInput(DjangoClearableFileInput):
    """
    A FileField Widget that shows its current value if it has one.
    If value is an Image, a thumbnail is shown.
    """
    
    initial_text = ugettext_lazy('Currently')
    input_text = ugettext_lazy('Change')
    clear_checkbox_label = ugettext_lazy('Clear')
    
    template_with_initial = u'<p class="file-upload">%(initial_text)s: %(initial)s<span class="clearable-file-input">%(clear_template)s</span><br />%(input_text)s: %(input)s %(preview)s</p>'
    template_with_clear = u'%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    # template_with_initial = u'%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'
    # template_with_clear = u'%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    # template_with_initial = (u'<p class="file-upload">%s</p>'% DjangoClearableFileInput.template_with_initial)
    # template_with_clear = (u'<span class="clearable-file-input">%s</span>'% DjangoClearableFileInput.template_with_clear)
    
    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'preview': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions['input'] = super(DjangoClearableFileInput, self).render(name, value, attrs)
        
        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = (u'<a target="_blank" href="%s">%s</a>' % (value.url, value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = checkbox_name
                substitutions['clear_checkbox_id'] = checkbox_id
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions
        
        if value and hasattr(value, "url"):
            preview_template = render_to_string('filebrowser/widgets/clearablefileinput.html', {
                'value': FileObject(value.name),
                'ADMIN_THUMBNAIL': ADMIN_THUMBNAIL,
            })
            substitutions["preview"] = preview_template
        
        return mark_safe(template % substitutions)


