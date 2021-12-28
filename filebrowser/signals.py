# coding: utf-8

from django.dispatch import Signal

# upload signals
# path: Absolute server path to the file/folder
# name: Name of the file/folder
# site: Current FileBrowserSite instance
filebrowser_pre_upload = Signal()
filebrowser_post_upload = Signal()

# mkdir signals
# path: Absolute server path to the file/folder
# name: Name of the file/folder
# site: Current FileBrowserSite instance
filebrowser_pre_createdir = Signal()
filebrowser_post_createdir = Signal()

# delete signals
# path: Absolute server path to the file/folder
# name: Name of the file/folder
# site: Current FileBrowserSite instance
filebrowser_pre_delete = Signal()
filebrowser_post_delete = Signal()

# rename signals
# path: Absolute server path to the file/folder
# name: Name of the file/folder
# site: Current FileBrowserSite instance
# new_name: New name of the file/folder
filebrowser_pre_rename = Signal()
filebrowser_post_rename = Signal()

# action signals
# action_name: Name of the custom action
# fileobjects: A list of fileobjects the action will be applied to
# site: Current FileBrowserSite instance
# result: The response you defined with your custom action
filebrowser_actions_pre_apply = Signal()
filebrowser_actions_post_apply = Signal()
