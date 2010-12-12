"""
group.py

Created by Paul Gower on 11/23/10.
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