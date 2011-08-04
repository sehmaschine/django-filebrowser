# coding: utf-8

# imports
import os.path
from exceptions import KeyError
from django.conf import settings
from django.core.cache import *
from time import time

# filebrowser imports
from filebrowser.settings import *
from filebrowser.base import *


class _GlobalVariableCache:
	"""
	This class implements a subset of the interface provided by the django's
	cache backends and can be used as their replacement.

	The advantage of _GlobalVarCache is that it avoids the overhead associated 
	with object pickling; obtaining a cached value is therefore signigicantly 
	faster than	with django's cache backends.

	The disadvantages stem from the fact, that an object of _GlobalVarCache is not 
	shared among processes, that is, no cross-process caching is possible. Further, 
	memory consumption can be an issue, because a server may employ multiple 
	processes to handle requests (each with its own cache) and no timeout is 
	employed to clean the cache. However, the consumed memory is practically constant 
	and limited by number of processes and the amount of cached directories and 
	their size. Finally, cached data do not persist over django's restarts.

	Note: This class is not meant to be used outside of the context of this 
	module.
	"""
	
	def __init__(self):
		self.cache = {}

	def has_key(self, key):
		return self.cache.has_key(key)

	def set(self, key, value):
		self.cache[key] = value

	def get(self, key):
		try:
			value = self.cache[key]
			return value
		except KeyError:
			return None

# Choose the cache
if hasattr(settings, 'CACHES') and settings.CACHES.has_key(FILEBROWSER_CACHE_NAME):
	cache = get_cache(FILEBROWSER_CACHE_NAME)
else:
	cache = _GlobalVariableCache()

def refresh_cache(folder_path):
	"""
	Refresh/create a cache for a given folder.
	"""
	# Create file listing
	filelisting = FileListing(folder_path)
	listing = filelisting.files_listing_total()
	# Go through the list and make FileObjects to read and store file parameters
	for fileobject in listing:
		_init_fileobject(fileobject)
	# Store the filelisting
	cache.set('[TIMESTAMP]' + folder_path, time())
	cache.set(folder_path, filelisting)
	
def is_cached(folder_path):
	"""
	Return True if the given folder is cached.
	"""
	# First try a quick look in cache
	if cache.has_key(folder_path):	
		return True
	# check for the marker file
	return os.path.exists(get_marker_path(folder_path))

def is_fresh(folder_path):
	"""
	Return True if the cache under a given folder path is up-to-date.
	"""
	if cache.has_key(folder_path):	
		timestamp = cache.get('[TIMESTAMP]' + folder_path)
		return timestamp > os.path.getmtime(folder_path)
	return False

def load_listing(folder_path):
	"""
	Load file listing from the cache of a given folder. Precondition: the folder is cached.
	"""
	listing = cache.get(folder_path)
	return listing

def update_cache_add(folder_path, new_file_path):
	"""Updates the cache of the folder at 'folder_path' by 
	adding a new file/folder to the listing."""
	listing = cache.get(folder_path)
	# Create and init new file object
	fileobject = FileObject(new_file_path)
	_init_fileobject(fileobject)
	listing._fileobjects_total.append(fileobject)
	# Update the cache
	cache.set('[TIMESTAMP]' + folder_path, time())
	cache.set(folder_path, listing)

def update_cache_remove(folder_path, file_path):
	"""Update the cache of the folder at 'folder_path' by 
	removing a file/folder from the listing. It is safe to 
	call this method even if the file under 'file_path' is
	not in the cached listing."""
	listing = cache.get(folder_path)
	# Find and remove the file from the listing
	for fileobject in listing._fileobjects_total:
		if fileobject.path == file_path:
			listing._fileobjects_total.remove(fileobject)
			break
	# Update the cache
	cache.set('[TIMESTAMP]' + folder_path, time())
	cache.set(folder_path, listing)

def update_cache_replace(folder_path, old_file_path, new_file_path):
	"""
	Update the cache of the folder at 'folder_path' by removing
	the file at 'old_file_path' and adding a new file at 'new_file_path'.
	Semantically same action as calling:
		update_cache_remove(folder_path, old_file_path)
		update_cache_add(folder_path, new_file_path)
	However, update_cache_replace() is significantly faster then the above approach
	when django's cache backends are used (due to the dalay caused by depickling of
	cached objects)
	"""
	listing = cache.get(folder_path)
	# Find and remove the old file from the listing
	for fileobject in listing._fileobjects_total:
		if fileobject.path == old_file_path:
			listing._fileobjects_total.remove(fileobject)
			break
	# Create and init the new file object
	fileobject = FileObject(new_file_path)
	_init_fileobject(fileobject)
	listing._fileobjects_total.append(fileobject)
	# Update the cache
	cache.set('[TIMESTAMP]' + folder_path, time())
	cache.set(folder_path, listing)
	

def update_cache_no_action(folder_path):
	"""Call this method to update the cache timestamp to current time. 
	In consequence, the cache is made fresh without any changes to cached data."""
	cache.set('[TIMESTAMP]' + folder_path, time())

def _init_fileobject(fileobject):
	"""Make a fileobject to read and store all the relevant parameters"""
	fileobject.filetype
	fileobject.filesize
	fileobject.date


def get_marker_path(folder_path):
	return os.path.join(folder_path, CACHE_MARKER_FILENAME)

