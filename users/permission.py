"""
permission.py

Created by Paul Gower on 11/27/10.
Copyright (c) 2010 Paul Gower. All rights reserved.

This file is part of PGUserManager.

PGUserManager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PGUserManager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PGUserManager.  If not, see <http://www.gnu.org/licenses/>.

Functions for manipulating Permissions
"""
import models
import exceptions
import utils
from google.appengine.api import memcache

def create_permission(name,description=None):
  """Create a new permission or raise a DuplicateValue exception if a permission already exists with that name"""
  key_name = name.lower()
  if models.Permission.get_by_key_name(key_name):
    raise exceptions.DuplicateValue(name)
  else:
    key = models.Permission(key_name=key_name,name=name,description=description).put()
    p = models.Permission.get(key)
    cache_key = name + '_permission'
    utils.add_dependants(cache_key,[p])
    memcache.set(cache_key,p)
    return p
    
def get_permission(name):
  """Return the given permission or none"""
  cache_key = name + '_permission'
  cache_value = memcache.get(cache_key)
  if cache_value:
    return cache_value
  else:
    p = models.Permission.get_by_key_name(name.lower())
    if p:
      utils.add_dependants(cache_key,[p])
      memcache.set(cache_key,p)
      return p
    else:
      return None
      
def permission_query(*args,**kwargs):
  """Return a query for permissions"""
  return models.Permission.all(*args,**kwargs)

    
      
  