from django.utils import six
from django.utils.module_loading import import_string

from .settings import VERSIONS, VERSION_NAMER


def get_namer(**kwargs):
    namer_cls = import_string(VERSION_NAMER)
    return namer_cls(**kwargs)


class VersionNamer(object):
    "Base namer only for reference"

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_version_name(self):
        return self.file_object.filename_root + "_" + self.version_suffix + self.extension

    def get_original_name(self):
        tmp = self.file_object.filename_root.split("_")
        if tmp[len(tmp) - 1] in VERSIONS:
            return u"%s%s" % (
                self.file_object.filename_root.replace("_%s" % tmp[len(tmp) - 1], ""),
                self.file_object.extension)


class OptionsNamer(VersionNamer):

    def get_version_name(self):
        name = "{root}_{options}{extension}".format(
            root=self.file_object.filename_root,
            options='--'.join(self.prepared_options),
            extension=self.file_object.extension,
        )
        return name

    def get_original_name(self):
        "Removes the substring containing the last _ (underscore) in the filename"
        root = self.file_object.filename_root
        tmp = root.split("_")
        options_part = tmp[len(tmp) - 1]
        return u"%s%s" % (root.replace("_%s" % options_part, ""), self.file_object.extension)

    @property
    def prepared_options(self):
        opts = []
        if not self.options:
            return opts

        if 'version_suffix' in self.kwargs:
            opts.append(self.kwargs['version_suffix'])

        if 'size' in self.options:
            opts.append('%sx%s' % tuple(self.options['size']))
        elif 'width' in self.options:
            opts.append('%sx%s' % (self.options['width'], self.options['width'],))

        for k, v in sorted(self.options.items()):
            if not v or k in ('size', 'width', 'height',
                              'quality', 'subsampling', 'verbose_name'):
                continue
            if v is True:
                opts.append(k)
                continue
            if not isinstance(v, six.string_types):
                try:
                    v = 'x'.join([six.text_type(v) for item in v])
                except TypeError:
                    v = six.text_type(v)
            opts.append('%s-%s' % (k, self.sanitize_value(v)))

        return opts

    def sanitize_value(self, value):
        return value.replace(',', 'x')
