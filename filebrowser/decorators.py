# coding: utf-8

# django imports
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.models import User
from django.template import RequestContext
from django.conf import settings


def flash_login_required(function):
    """
    Decorator to recognize a user  by its session.
    Used for Flash-Uploading.
    """
    
    def decorator(request, *args, **kwargs):
        try:
            engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        except:
            import django.contrib.sessions.backends.db
            engine = django.contrib.sessions.backends.db
        session_data = engine.SessionStore(request.POST.get('session_key'))
        user_id = session_data['_auth_user_id']
        # will return 404 if the session ID does not resolve to a valid user
        request.user = get_object_or_404(User, pk=user_id)
        return function(request, *args, **kwargs)
    return decorator


