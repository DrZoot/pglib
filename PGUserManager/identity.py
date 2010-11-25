"""
identity.py

Created by Paul Gower on 11/23/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating identities
"""
import models
from google.appengine.api import User
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
  --Description--
  Creates a new identity in the data store. Returns the saved identity so that extra properties can be added.
  If given an identity that is already used then raises a EmailAddressAlreadyUsed exception with the name of the 
  existing identity as the argument.
  --Arguments--
  email_address : String : Mandatory string specifying the email address to use when creating the identity.
  --Returns--
  saved identity model object
  """
  return models.Identity(email=email_address,user=).put()

def get_identity(email_address):
  """
  --Description--
  Get an identity from the store. If given a list return a list of matching identities.
  Raise an identity does not exists exception if an email address is passed that does not exist.
  """
  pass
  
def identity_query(*args,**kwargs):
  """
  Equivalent to Identity.all(*args,**kwargs)
  """
  return models.Identity.all(*args,**kwargs)
  