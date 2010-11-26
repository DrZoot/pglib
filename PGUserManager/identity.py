"""
identity.py

Created by Paul Gower on 11/23/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating identities
"""
import models
import exceptions
"""
http://stackoverflow.com/questions/1054868/recursive-delete-in-google-app-engine

You need to implement this manually, by looking up affected records and deleting them at the same time as you delete the parent record. You can simplify this, if you wish, by overriding the .delete() method on your parent class to automatically delete all related records.

For performance reasons, you almost certainly want to use key-only queries (allowing you to get the keys of entities to be deleted without having to fetch and decode the actual entities), and batch deletes. For example:

db.delete(Bottom.all(keys_only=True).filter("daddy =", top).fetch(1000))
"""
# =============
# = Functions =
# =============

def create_identity(email_address):
  """
  Creates a new identity in the datstore and returns the identity object or if the email has already been used raises an AddressAlreadyUsed exception with the 
  """
  uniqueness_query = models.Identity.all(keys_only=True).filter('email',email_address)
  if uniqueness_query.get():
    raise exceptions.AddressAlreadyUsed(email_address)
  else:
    key = models.Identity(key_name=email_address,email=email_address).put()
    return models.Identity.get(key)

def get_identity(email_address):
  """
  Given an email address try to return a datastore object for it using the email_address as a key_name
  """
  return models.Identity.get_by_key_name(email_address)
  
def identity_query(*args,**kwargs):
  """
  Equivalent to Identity.all(*args,**kwargs). Used here to shield Identity from having to be directly imported outside the module.
  """
  return models.Identity.all(*args,**kwargs)