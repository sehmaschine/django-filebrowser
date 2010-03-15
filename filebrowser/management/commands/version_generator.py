from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "(Re)Generate versions of Images"

    def handle_noargs(self, **options):
        import os, re
        from filebrowser.settings import EXTENSION_LIST, EXCLUDE, MEDIA_ROOT, DIRECTORY, VERSIONS, EXTENSIONS
        
        # Precompile regular expressions
        filter_re = []
        for exp in EXCLUDE:
           filter_re.append(re.compile(exp))
        for k,v in VERSIONS.iteritems():
            exp = (r'_%s.(%s)') % (k, '|'.join(EXTENSION_LIST))
            filter_re.append(re.compile(exp))
            
        path = os.path.join(MEDIA_ROOT, DIRECTORY)
        
        # walkt throu the filebrowser directory
        # for all/new files (except file versions itself and excludes)
        for dirpath,dirnames,filenames in os.walk(path):
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
                    self.createVersions(os.path.join(dirpath, filename))
    
    def createVersions(self, path):
        print "generating versions for: ", path
        from filebrowser.settings import VERSIONS
        from filebrowser.functions import version_generator
        for version in VERSIONS:
            #print "                          ", version
            version_generator(path, version, True)
