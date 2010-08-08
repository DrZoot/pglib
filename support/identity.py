"""
identity.py

Created by Paul Gower on 08/07/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Support functions for identity - user operations
"""
from model.identity import Identity
from model.group import Group
from google.appengine.api import users

def user_identity(user=None):
  """create or retrieve an identity for the current user"""
  if not user:
    user = users.get_current_user()
  identity_query = Identity.all().filter('user',user)
  if identity_query.count() > 0:
    return identity_query.get()
  else:
    new_id = Identity(user=user)
    new_id.put()
    # add to default groups
    viewers = Group.all().filter('name','Viewers').get()
    viewers.members.append(new_id.key())
    viewers.put()
    return new_id
    
def user_domain(user=None):
  """return the domain of the current user (everything after the @)"""
  if not user:
    user = users.get_current_user()
  email = user.email()
  domain = email.split('@')[1]
  return domain
  