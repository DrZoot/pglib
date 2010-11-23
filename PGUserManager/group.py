"""
group.py

Created by Paul Gower on 11/23/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating groups
"""
def create_group(name,description=None):
  """docstring for create_group"""
  if not description:
    description = ""
  pass
  
def delete_group(name,):
  """docstring for delete_group"""
  pass
  


class NameAlreadyUsed(Exception):
  """
  --Description--
  Raised if someone tries to create a group with a name that already exists.
  """
  def __init__(self,value):
    self.value = value

  def __str__(self):
    return repr(self.value)
    