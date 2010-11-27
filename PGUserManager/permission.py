"""
permission.py

Created by Paul Gower on 11/27/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating Permissions
"""
import models
import exceptions

def create_permission(name,description=None):
  """Create a new permission or raise a NameAlreadyUsed exception if a permission already exists with that name"""
  uniqueness_query = models.Permission.all(keys_only=True).filter('name',name)
  if uniqueness_query.get():
    raise exceptions.NameAlreadyUsed(name)
  else:
    key = models.Permission(key_name=name,name=name,description=description).put()
    return models.Permission.get(key)
    
def get_permission(name):
  """Return the given permission or none"""
  return models.Permission.all().filter('name',name).get()
  
def permission_query(*args,**kwargs):
  """Return a query for permissions"""
  return models.Permission.all(*args,**kwargs)
  
def bind_permission(permission,subject):
  """Create a permission binding between the given permission and the subject (group/identity)"""
  if not isinstance(permission,models.Permission):
    raise Exception("Must pass permission object, not key.")
  else:
    permission_name = permission.name
  if not isinstance(subject,models.Identity) or not isinstance(subject,models.Group):
    raise Exception("Must pass either an Identity object or a Group object, not keys.")
  else:
    subject_name = subject.key().name
  permission_binding_name = permission_name + "_" + subject_name
  if models.PermissionBinding.get_by_key_name(permission_binding_name):
    raise Exception("PermissionBinding already exists")
  else:
    key = models.PermissionBinding(key_name=permission_binding_name,permission=permission,subject=subject).put()
    return models.PermissionBinding.get(key)
      
  