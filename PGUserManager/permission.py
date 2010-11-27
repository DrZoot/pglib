"""
permission.py

Created by Paul Gower on 11/27/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating Permissions
"""
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