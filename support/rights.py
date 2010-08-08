"""
rights.py

Created by Paul Gower on 08/07/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Support functions for user/group rights
"""
from google.appengine.api import users
from model.right import Right

from support.identity import user_identity
from support.groups import user_groups

def user_has_right(right_name, user=None):
  """Returns true if the given user has the named right (user defaults to current)"""
  if not user:
    user = users.get_current_user()
  if users.is_current_user_admin():
    # if user is a domain admin they get all rights
    return True
  else:
    identity = user_identity()
    groups = user_groups()
    rights_query = Right.all().filter('name',right_name).filter('holders IN', groups)
    if rights_query.count() > 1:
      # belong to a group with the named right
      return True
    else:
      return False
  