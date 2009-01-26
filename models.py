# -*- coding: UTF-8 -*-
import os
from datetime import datetime
from inspect import isclass

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.functional import lazy
from django.core.files import base

from filebrowser.functions import path_exists, locate
from filebrowser.fields import FileBrowseField
from filebrowser.fb_settings import *

# TODO: do we really need dependencies on third-party modules?
#from tagging.fields import TagField 

FILE_TYPE_CHOICES = [(item, _(item)) for item in EXTENSIONS.keys()]

# Required PIL classes may or may not be available from the root namespace
# depending on the installation method used.
try:
    import Image
    import ImageFile
    import ImageOps
    import ImageFilter
    import ImageEnhance
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageFile
        from PIL import ImageOps
        from PIL import ImageFilter
        from PIL import ImageEnhance
    except ImportError:
        raise ImportError(_('Filebrowser was unable to import the Python Imaging Library. Please confirm it`s installed and available on your current Python path.'))

# Modify image file buffer size.
ImageFile.MAXBLOCK = IMAGE_MAXBLOCK

# Prepare a list of image filters
filter_names = []
for n in dir(ImageFilter):
    klass = getattr(ImageFilter, n)
    if isclass(klass) and issubclass(klass, ImageFilter.BuiltinFilter) and hasattr(klass, 'name'):
        filter_names.append(klass.__name__)
image_filters_help_text = _('Chain multiple filters using the following pattern "FILTER_ONE->FILTER_TWO->FILTER_THREE". Image filters will be applied in order. The following filter are available: %s') % ', '.join(filter_names)

# Quality options for JPEG images
JPEG_QUALITY_CHOICES = (
    (30, _('Very Low')),
    (40, _('Low')),
    (50, _('Medium-Low')),
    (60, _('Medium')),
    (70, _('Medium-High')),
    (80, _('High')),
    (90, _('Very High')),
)

# choices for new crop_anchor field in Photo
CROP_ANCHOR_CHOICES = (
    ('top', _('Top')),
    ('right', _('Right')),
    ('bottom', _('Bottom')),
    ('left', _('Left')),
    ('center', _('Center (Default)')),
)

OUTPUT_FORMAT_CHOICES = (
    ('png', 'PNG'),
    ('jpg', 'JPEG'),
    ('gif', 'GIF'),
)

class FileManager(models.Manager):
    def save_file(self, path, content, **kwargs):
        """
        Save media file and create a thumbnail for the filebrowser and
        the related File object
        """
        abs_path = os.path.join(PATH_SERVER, *path.split("/"))
        abs_dir, filename = os.path.split(abs_path)
        path_exists(abs_dir)
        filename_base, filename_ext = os.path.splitext(filename)
        
        f = open(abs_path, 'wb')
        if isinstance(content, base.File):
            for chunk in content.chunks():
                f.write(chunk)
        else:
            f.write(content)
        f.close()
        try:
            file_obj = self.get(
                path=path,
                )
        except:
            file_obj = self.model(
                path=path,
                )
        file_type = ""
        for k, v in EXTENSIONS.iteritems():
            for ext in v:
                if ext == filename_ext:
                    file_type = k
        file_timestamp = datetime.fromtimestamp(
            os.path.getmtime(abs_path)
            )
        file_obj.uploaded = file_timestamp
        width = height = 0
        if file_type == 'Image':
            tn_file_path = os.path.join(
                path_exists(abs_dir, "_cache"),
                "%s%s.png" % (THUMB_PREFIX, filename),
                )
            try:
                im = Image.open(abs_path)
                if im.mode != "RGB":
                    im = im.convert("RGB")
                width = im.size[0]
                height = im.size[1]
                im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                im.save(tn_file_path)
            except IOError:
                pass
        
        file_obj.file_type = file_type
        if isinstance(content, base.File):
            file_obj.size = content.size
        else:
            file_obj.size = len(content)
        file_obj.width = width
        file_obj.height = height
        for key, value in kwargs.items():
            setattr(file_obj, key, value)
        file_obj.save()
        return file_obj
        
    def delete_file(self, path):
        """
        Delete media file or directory, the related File object,
        and all its modifications
        """
        abs_path = os.path.join(PATH_SERVER, *path.split("/"))
        abs_dir, filename = os.path.split(abs_path)
        self.filter(path=path).delete()
        if os.path.isdir(abs_path):
            abs_cache_dir = os.path.join(abs_path, "_cache")
            if os.path.isdir(abs_cache_dir):
                for mod_file_path in locate("*", abs_cache_dir):
                    os.unlink(mod_file_path)
                os.rmdir(abs_cache_dir)
            os.rmdir(abs_path)
        else:
            filename_base, filename_ext = os.path.splitext(filename)
            abs_cache_dir = os.path.join(abs_dir, "_cache")
            for tn_file_path in locate( 
                "%s%s.png" % (THUMB_PREFIX, filename),
                abs_cache_dir,
                ):
                os.unlink(tn_file_path)
            for mod_file_path in locate(
                "%s_*" % filename,
                abs_cache_dir,
                ):
                os.unlink(mod_file_path)
            os.unlink(abs_path)
            
    def save_file_for_object(
        self,
        obj,
        filename,
        content,
        field_name="image",
        subpath="", # if not empty, must have a trailing slash
        use_timestamp=True,
        replace_existing=True,
        ):
        """
        Saves media file for an object and assigns the relative
        filebrowser path of the file to the specified field of the object.
        
        The absolute path of the file:
        PATH_SERVER + obj.get_filebrowser_path() + subpath + mediafile.filename        
        """
        if replace_existing:
            self.delete_file_for_object(obj, field_name)
        filename_base, filename_ext = os.path.splitext(filename)
        if use_timestamp:
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + filename_ext
                
        path = ""
        if hasattr(obj, "get_filebrowser_dir"):
            if callable(obj.get_filebrowser_dir):
                path += obj.get_filebrowser_dir()
        if subpath:
            path += subpath
        path += filename
        File.objects.save_file(path, content)
        setattr(obj, field_name, path)
        super(type(obj), obj).save()

    def delete_file_for_object(self, obj, field_name="image"):
        """
        Delete media file for an object
        """
        path = getattr(obj, field_name)
        if path:
            try:
                self.delete_file(path)
            except OSError:
                pass
            setattr(obj, field_name, "")
        super(type(obj), obj).save()


class File(models.Model):
    path = models.TextField(_("File Path"), editable=False)
    
    #tags = TagField(_("Tags"), blank=True, null=True)
    
    uploader = models.ForeignKey(User, verbose_name=_("Uploader"), null=True, blank=True)
    
    title = models.CharField(_('title'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)
    
    width = models.PositiveIntegerField(_("Width"), blank=True, null=True, editable=False)
    height = models.PositiveIntegerField(_("Height"), blank=True, null=True, editable=False)
    size = models.PositiveIntegerField(_("Size in bytes"), blank=True, null=True, editable=False)
    
    uploaded = models.DateTimeField(_("Uploaded"), null=True, editable=False)
    created = models.DateTimeField(_("Created"), auto_now_add=True, null=True, editable=False)
    modified = models.DateTimeField(_("Modified"), null=True, editable=False, auto_now=True)
    
    file_type = models.CharField(_("File Type"), blank=True, choices=FILE_TYPE_CHOICES, max_length=30, editable=False)
    
    objects = FileManager()

    class Meta:
        verbose_name = _("file")
        verbose_name_plural = _("files")
        permissions = (
            ("browse_file", "Can browse file"),
            ("make_dir", "Can create directories"),
            )

    def __unicode__(self):
        return force_unicode(self.path)

    def get_filename_base(self):
        filename_base, filename_ext = os.path.splitext(self.get_filename())
        return filename_base
        
    def get_filename_ext(self):
        filename_base, filename_ext = os.path.splitext(self.get_filename())
        return filename_ext

    def get_filename(self):
        abs_path = os.path.join(PATH_SERVER, *self.path.split("/"))
        abs_dir, filename = os.path.split(abs_path)
        return filename
        
    def get_abs_dir(self):
        abs_path = os.path.join(PATH_SERVER, *self.path.split("/"))
        abs_dir, filename = os.path.split(abs_path)
        return abs_dir
        
    def get_dir_name(self):
        bits = self.path.rsplit("/", 1)
        dir_name = ""
        if len(bits)>1:
            dir_name = bits[0]
        return dir_name

    def get_filesize(self):
        """
        Get filesize in a readable format.
        """
        filesize_str = ""
        if self.size < 1024:
            filesize_str = "%s B" % self.size
        elif self.size >= 1024 and self.size < 1024*1024:
            filesize_str = "%s KB" % (self.size/1024)
        elif self.size >= 1024*1024:
            filesize_str = "%s MB" % (self.size/(1024*1024))
        return filesize_str
        
    def get_thumbnail_url(self):
        thumb_path = ""
        if os.path.isfile(self.get_thumbnail_path()):
            rel_dir, filename = os.path.split(self.path)
            thumb_path = "%s%s/_cache/%s%s.png" % (URL_WWW, rel_dir, THUMB_PREFIX, filename)
        return thumb_path
        
    def get_thumbnail_path(self):
        abs_path = os.path.join(PATH_SERVER, *self.path.split("/"))
        abs_dir, filename = os.path.split(abs_path)
        return os.path.join(
            abs_dir, "_cache",
            "%s%s.png" % (THUMB_PREFIX, filename),
            )

class ImageModification(models.Model):
    """ A pre-defined effect to apply to image files """
    sysname = models.SlugField(_("Sysname"), max_length=255, help_text=_("Sysnames are used for cached file suffixes and in the templates"))
    
    title = models.CharField(_('title'), max_length=255)
    
    width = models.PositiveIntegerField(_('width'), default=0, help_text=_('Leave to size the image to the set height'))
    height = models.PositiveIntegerField(_('height'), default=0, help_text=_('Leave to size the image to the set width'))
    quality = models.PositiveIntegerField(_('quality'), choices=JPEG_QUALITY_CHOICES, default=70, help_text=_('JPEG image quality.'))
    crop = models.BooleanField(_('crop to fit?'), default=False, help_text=_('If selected the image will be scaled and cropped to fit the supplied dimensions.'))
    crop_from = models.CharField(_('crop from'), blank=True, max_length=10, default='center', choices=CROP_ANCHOR_CHOICES)

    mask = FileBrowseField(_("Mask"), max_length=255, extensions_allowed=['.png'], blank=True, null=True)
    
    frame = FileBrowseField(_("Frame"), max_length=255, extensions_allowed=['.png'], blank=True, null=True)

    output_format = models.CharField(_("Output format"), max_length=255, default="png", choices=OUTPUT_FORMAT_CHOICES)

    color = models.FloatField(_('color'), default=1.0, help_text=_('A factor of 0.0 gives a black and white image, a factor of 1.0 gives the original image.'))
    brightness = models.FloatField(_('brightness'), default=1.0, help_text=_('A factor of 0.0 gives a black image, a factor of 1.0 gives the original image.'))
    contrast = models.FloatField(_('contrast'), default=1.0, help_text=_('A factor of 0.0 gives a solid grey image, a factor of 1.0 gives the original image.'))
    sharpness = models.FloatField(_('sharpness'), default=1.0, help_text=_('A factor of 0.0 gives a blurred image, a factor of 1.0 gives the original image.'))
    filters = models.CharField(_('filters'), max_length=200, blank=True, help_text=image_filters_help_text)
    
    class Meta:
        verbose_name = _("Image Modification")
        verbose_name_plural = _("Image Modifications")
        ordering = ("sysname",)
    
    def __unicode__(self):
        return self.title

    def get_title(self):
        return self.title

    def delete_cached_images(self):
        """ delete the cached images of this modification """
        for path in locate("*_%s.*" % self.sysname, PATH_SERVER):
            file_dir, filename = os.path.split(path)
            if os.path.split(file_dir)[1] == "_cache":
                try:
                    os.unlink(path)
                except OSError:
                    pass

    def save(self, *args, **kwargs):
        super(type(self), self).save(*args, **kwargs)
        self.delete_cached_images()

    def delete(self):
        super(type(self), self).delete()
        self.delete_cached_images()

    def modified_path(self, path):
        if "/" in path:
            dir_name, filename = path.rsplit("/", 1)
            dir_name += "/"
        else:
            dir_name, filename = "", path
        mod_path = "%s_cache/%s_%s.%s" % (
            dir_name,
            filename,
            self.sysname,
            self.output_format,
            )
        return mod_path
        
    def process_image(self, absolute_original_path):
        try:
            im = Image.open(absolute_original_path)
        except IOError:
            return False
        if im.mode != "RGB":
            im = im.convert("RGB")
        cur_width, cur_height = im.size
        new_width, new_height = self.width, self.height

        if self.crop:
            ratio = max(float(new_width)/cur_width,float(new_height)/cur_height)
            x = (cur_width * ratio)
            y = (cur_height * ratio)
            xd = abs(new_width - x)
            yd = abs(new_height - y)
            x_diff = int(xd / 2)
            y_diff = int(yd / 2)
            if self.crop_from == 'top':
                box = (int(x_diff), 0, int(x_diff+new_width), new_height)
            elif self.crop_from == 'left':
                box = (0, int(y_diff), new_width, int(y_diff+new_height))
            elif self.crop_from == 'bottom':
                box = (int(x_diff), int(yd), int(x_diff+new_width), int(y)) # y - yd = new_height
            elif self.crop_from == 'right':
                box = (int(xd), int(y_diff), int(x), int(y_diff+new_height)) # x - xd = new_width
            else:
                box = (int(x_diff), int(y_diff), int(x_diff+new_width), int(y_diff+new_height))
            resized = im.resize((int(x), int(y)), Image.ANTIALIAS).crop(box)
        else:
            if not new_width == 0 and not new_height == 0:
                ratio = min(
                    float(new_width)/cur_width,
                    float(new_height)/cur_height,
                    )
            else:
                if new_width == 0:
                    ratio = float(new_height)/cur_height
                else:
                    ratio = float(new_width)/cur_width
            resized = im.resize(
                (int(round(cur_width*ratio)), int(round(cur_height*ratio))),
                Image.ANTIALIAS,
                )
        
        if resized.mode == 'RGB':
            for name in ['Color', 'Brightness', 'Contrast', 'Sharpness']:
                factor = getattr(self, name.lower())
                if factor != 1.0:
                    resized = getattr(ImageEnhance, name)(resized).enhance(factor)
            for name in self.filters.split('->'):
                image_filter = getattr(ImageFilter, name.upper(), None)
                if image_filter is not None:
                    try:
                        resized = resized.filter(image_filter)
                    except ValueError:
                        pass
                    
        if self.mask:
            try:
                mask = Image.open(
                    os.path.join(PATH_SERVER, *self.mask.split("/")),
                    )
            except:
                pass
            else:
                resized = resized.convert("RGBA")
                # resize/crop the image to the size of the mask-image
                resized = ImageOps.fit(resized, mask.size, method=Image.ANTIALIAS)    
                # get the alpha-channel (used for non-replacement)
                r,g,b,a = mask.split()
                resized.paste(mask, mask=a)
            
        if self.frame:
            try:
                frame = Image.open(
                    os.path.join(PATH_SERVER, *self.frame.split("/")),
                    )
            except:
                pass
            else:
                resized = resized.convert("RGBA")
                # resize/crop the image to the size of the mask-image
                resized = ImageOps.fit(resized, mask.size, method=Image.ANTIALIAS)    
                # paste the frame mask without replacing the alpha mask of the mask-image
                r,g,b,a = frame.split()
                resized.paste(frame, mask=a)

        absolute_resized_path = self.modified_path(absolute_original_path)

        try:
            if im.format == 'JPEG':
                resized.save(
                    absolute_resized_path,
                    'JPEG',
                    quality=int(self.quality),
                    optimize=True,
                    )
            else:
                resized.save(absolute_resized_path)
        except IOError, e:
            if os.path.isfile(absolute_resized_path):
                os.unlink(absolute_resized_path)
            return False #raise e
            
        return True
        