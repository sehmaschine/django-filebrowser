from django.conf import settings
from django.http.response import Http404
from django.shortcuts import redirect
from filebrowser.base import FileObject


class OnDemandMiddleware(object):
    """
    Middleware that handles 404 errors of images and generates missing image versions.

    If the new version is successfully generated, redirects to generated version url.
    This make sure new request is made by browser, and  file serving will be done
    in ordinary way (probably by web-server).

    Just make sure the web-server request is handled by django if the requested file does not exist.
    """

    def process_exception(self, request, exception):
        # Check that exception is 404 error for file in media folder
        if isinstance(exception, Http404) and request.path.startswith(settings.MEDIA_URL):
            # Strip MEDIA_URL from path and test if requested path is image version
            # with existing original image
            relative_path = request.path[len(settings.MEDIA_URL):]
            file_obj = FileObject(relative_path)
            if file_obj.is_version:
                original_obj = file_obj.original
                if original_obj.exists:
                    # Generate requested image version
                    new_file_obj = original_obj.version_generate(file_obj.version)

                    # Redirects to generated image URL
                    return redirect(new_file_obj.url)