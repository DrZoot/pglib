"""
group.py

Created by Paul Gower on 11/23/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating groups
"""
import models
import exceptions
import utils

def create_group(name,description=None):
  """create a group with the given name, if a group with the same name exists raise """
  key_name = name.lower()
  if models.Group.get_by_key_name(key_name):
    raise exceptions.DuplicateValue(name)
  else:
    key = models.Group(key_name=key_name,name=name,description=description).put()
    return models.Group.get(key)
  
def get_group(name):
  """return the group with the given name or none"""
  return models.Group.get_by_key_name(name.lower())
  
def group_query(*args,**kwargs):
  """return a query for groups"""
  return models.Group.all(*args,**kwargs)