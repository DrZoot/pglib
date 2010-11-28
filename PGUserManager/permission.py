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
  uniqueness_query = models.Permission.all(keys_only=True).filter('name',name)
  if uniqueness_query.get():
    raise exceptions.DuplicateValue(name)
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
  permission = utils.verify_arg(permission,models.Permission)
  subject = utils.verify_arg(subject,models.Identity,models.Group)
  permission_binding_name = permission.name + "_" + subject.key().name
  if models.PermissionBinding.get_by_key_name(permission_binding_name):
    raise exceptions.BindingExists("PermissionBinding already exists")
  else:
    key = models.PermissionBinding(key_name=permission_binding_name,permission=permission,subject=subject).put()
    return models.PermissionBinding.get(key)
    
def unbind_permission(permission,subject):
  """remove permission bindings for the given permission and subject"""
  permission = utils.verify_arg(permission,models.Permission)
  subject = utils.verify_arg(subject,models.Identity,models.Group)
  permission_binding_name = permission.name + "_" + subject.key().name
  binding = models.PermissionBinding.get_by_key_name(permission_binding_name)
  if binding:
    binding.delete()
    # if we found a binding and deleted it return true
    return True
  else:
    # if we did not find a binding return None, no exception because the bindings are in the state expected
    return None
    
def unbind_permission_from_subjects(permission,subjects):
  """remove 1 permission from multiple subjects"""
  pass
  
def unbind_permissions_from_subject(permissions,subject):
  """remove many permissions from 1 subject"""
  pass

    
      
  