# coding: utf-8

# DJANGO IMPORTS
from django.dispatch import Signal

# mkdir signals
filebrowser_pre_createdir = Signal(providing_args=["path", "name"])
filebrowser_post_createdir = Signal(providing_args=["path", "name"])

# delete signals
filebrowser_pre_delete = Signal(providing_args=["path", "name"])
filebrowser_post_delete = Signal(providing_args=["path", "name"])

# rename signals
filebrowser_pre_rename = Signal(providing_args=["path", "name", "new_name"])
filebrowser_post_rename = Signal(providing_args=["path", "name", "new_name"])

# action signals
filebrowser_actions_pre_apply = Signal(providing_args=['action_name', 'fileobjects',])
filebrowser_actions_post_apply = Signal(providing_args=['action_name', 'filebjects', 'result'])

# upload signals
filebrowser_pre_upload = Signal(providing_args=["path", "file"])
filebrowser_post_upload = Signal(providing_args=["path", "file"])