"""
identity.py

Created by Paul Gower on 11/23/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating identities
"""
import models
import exceptions
from google.appengine.api import users

def create_identity(email_address,active=True,**kwargs):
  """
  Creates a new identity in the datstore and returns the identity object or if the email has already been used raises an DuplicateValue exception 
  """
  key_name = email_address.lower()
  if models.Identity.get_by_key_name(key_name):
    raise exceptions.DuplicateValue(email_address)
  else:
    key = models.Identity(key_name=key_name,email=email_address,active=active,**kwargs).put()
    return models.Identity.get(key)

def get_identity(email_address,include_inactive=False):
  """
  Given an email address try to return a datastore object for it using the email_address as a key_name
  """
  i = models.Identity.get_by_key_name(email_address.lower())
  if i == None:
    return None
  elif i.active:
    return i
  else:
    if include_inactive:
      return i
    else:
      return None
  
def identity_query(*args,**kwargs):
  """
  Equivalent to Identity.all(*args,**kwargs). Used here to shield Identity from having to be directly imported outside the module.
  """
  return models.Identity.all(*args,**kwargs)
  
def identity_for_current_user():
  """Return the identity for the currently logged on user or None"""
  key_name = users.get_current_user().email().lower()
  return get_identity(key_name)