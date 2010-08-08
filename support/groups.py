"""
groups.py

Created by Paul Gower on 08/07/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Groups support functions
"""
from google.appengine.api import users
from support.identity import user_identity, user_domain
from model.group import Group

def user_groups(user=None):
  """return a list of groups the user belongs to (user defaults to current)"""
  if not user:
    user = users.get_current_user()
  identity = user_identity()
  domain = user_domain()
  groups_query = Group.all().filter('domain',domain).filter('members',identity.key())
  result = []
  for group in groups_query:
    result.append(group)
  return result

  