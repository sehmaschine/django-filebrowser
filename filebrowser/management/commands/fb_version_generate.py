# coding: utf-8

# PYTHON IMPORTS
import os, re

# DJANGO IMPORTS
from django.core.management.base import BaseCommand, CommandError

# FILEBROWSER IMPORTS
from filebrowser.settings import EXTENSION_LIST, EXCLUDE, MEDIA_ROOT, DIRECTORY, VERSIONS, EXTENSIONS
from filebrowser.functions import version_generator


class Command(BaseCommand):
    args = '<media_path>'
    help = "(Re)Generate Image-Versions within FILEBROWSER_DIRECTORY/MEDIA_ROOT."
    
    def handle(self, *args, **options):
        media_path = ""
        
        if len(args):
            media_path = args[0]
            path = os.path.join(MEDIA_ROOT, media_path)
        else:
            path = os.path.join(MEDIA_ROOT, DIRECTORY)
        
        if not os.path.isdir(path):
            raise CommandError('<media_path> must be a directory in MEDIA_ROOT (If you don\'t add a media_path the default path is FILEBROWSER_DIRECTORY).\n"%s" is no directory.' % path);
        
        # get version name
        while 1:
            self.stdout.write('\nSelect a version you want to generate:\n')
            for version in VERSIONS:
                self.stdout.write(' * %s\n' % version)
            
            version_name = raw_input('(leave blank to generate all versions): ')
            
            if version_name == "":
                selected_version = None
                break
            else:
                try:
                    tmp = VERSIONS[version_name]
                    selected_version = version_name
                    break
                except:
                    self.stderr.write('Error: Version "%s" doesn\'t exist.\n' % version_name)
                    version_name = None
                    continue
        
        # Precompile regular expressions
        filter_re = []
        for exp in EXCLUDE:
           filter_re.append(re.compile(exp))
        for k,v in VERSIONS.iteritems():
            exp = (r'_%s(%s)') % (k, '|'.join(EXTENSION_LIST))
            filter_re.append(re.compile(exp))
        
        # walkt throu the filebrowser directory
        # for all/new files (except file versions itself and excludes)
        for dirpath,dirnames,filenames in os.walk(path, followlinks=True):
            for filename in filenames:
                filtered = False
                # no "hidden" files (stating with ".")
                if filename.startswith('.'):
                    continue
                # check the exclude list
                for re_prefix in filter_re:
                    if re_prefix.search(filename):
                        filtered = True
                if filtered:
                    continue
                (tmp, extension) = os.path.splitext(filename)
                if extension in EXTENSIONS["Image"]:
                    self.createVersions(os.path.join(dirpath, filename), selected_version)
    
    def createVersions(self, path, selected_version):
        if selected_version:
            self.stdout.write('generating version "%s" for: %s\n' % (selected_version, path))
            version_generator(path, selected_version, True)
        else:
            self.stdout.write('generating all versions for: %s\n' % path)
            for version in VERSIONS:
                version_generator(path, version, True)


