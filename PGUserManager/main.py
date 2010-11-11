"""
main.py

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

PGUserManager - User management API that uses BigTable for storage.
"""
from google.appengine.api import users
import models #TODO: check this works, may need to fanagle the import path

# Public 

#--User Functions-- 
def userHasPermission(permission, user=None):
  """
  If no user is passed then the current logged on user is assumed.
  Given a user return true if the user has the specified permission or false if not.
  If a user is part of a group that has access to this permission this also counts.
  """
  
def userGroups(user=None):
  """
  Return a list of objects for groups that a user belongs to.
  """
  
def userInGroup(
#--Group Functions--
def groupHasPermission(group, permission)

#--Permission Functions--


# Private
