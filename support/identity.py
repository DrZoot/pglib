"""
identity.py

Created by Paul Gower on 08/07/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Support functions for identity - user operations
"""
from model.identity import Identity
from model.group import Group
from model.domain import Domain
from google.appengine.api import users

def is_current_user_admin():
  """Just calls users.is_current_user_admin()"""
  return users.is_current_user_admin()

def user_identity(user=None):
  """create or retrieve an identity for the current user"""
  if not user:
    user = users.get_current_user()
  identity = Identity.all().filter('user',users.get_current_user()).get()
  return identity
    
def create_identity(user=None):
  """create an identity for a user (defaults to current)"""
  if not user:
    user = users.get_current_user()
  domain = user_domain()
  identity = Identity(user=user,domain=domain)
  identity.put()
  # add to default groups
  viewers = Group.all().filter('domain',domain).filter('name','Viewers').get()
  viewers.members.append(identity.key())
  viewers.put()
    
def user_domain_name(user=None):
  """return the domain name of the current user (everything after the @)"""
  if not user:
    user = users.get_current_user()
  email = user.email()
  domain_name = email.split('@')[1]
  return domain_name
  
def user_domain(user=None):
  """return the domain object of the given user (defaults to current)"""
  if not user:
    user = users.get_current_user()
  domain_name = user_domain_name()
  domain = Domain.all().filter('name',domain_name).get()
  return domain
  
  