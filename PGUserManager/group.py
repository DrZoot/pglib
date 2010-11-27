"""
group.py

Created by Paul Gower on 11/23/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating groups
"""
import models
import exceptions

def create_group(name,description=None):
  """create a group with the given name, if a group with the same name exists raise """
  uniqueness_query = models.Group.all(keys_only=True).filter('name',name)
  if uniqueness_query.get():
    raise exceptions.NameAlreadyUsed(name)
  else:
    key = models.Group(key_name=name,name=name,description=description).put()
    return models.Group.get(key)
  
  
def get_group(name):
  """return the group with the given name or none"""
  return models.Group.all().filter('name',name).get()
  
def group_query(*args,**kwargs):
  """return a query for groups"""
  return models.Group.all(*args,**kwargs)
    