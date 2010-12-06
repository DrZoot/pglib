"""
permission.py

Created by Paul Gower on 11/27/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating Permissions
"""
import models
import exceptions
import utils

def create_permission(name,description=None):
  """Create a new permission or raise a DuplicateValue exception if a permission already exists with that name"""
  key_name = name.lower()
  if models.Permission.get_by_key_name(key_name):
    raise exceptions.DuplicateValue(name)
  else:
    key = models.Permission(key_name=key_name,name=name,description=description).put()
    return models.Permission.get(key)
    
def get_permission(name):
  """Return the given permission or none"""
  return models.Permission.get_by_key_name(name.lower())
  
def permission_query(*args,**kwargs):
  """Return a query for permissions"""
  return models.Permission.all(*args,**kwargs)
  
def unbind_permission_from_subjects(permission,subjects):
  """remove 1 permission from multiple subjects"""
  pass
  
def unbind_permissions_from_subject(permissions,subject):
  """remove many permissions from 1 subject"""
  pass

    
      
  