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

def create_identity(email_address, properties=None):
  """
  --Description--
  Creates a new identity in the data store. If passed a dictionary of properties these are stored with the identity.
  If given an identity that is already used then raises a EmailAddressAlreadyUsed exception with the name of the 
  existing identity as the argument.
  --Arguments--
  email_address : String : Mandatory string specifying the email address to use when creating the identity.
  properties : Dictionary : Optional dictionary of key:value properties to store with the identity. Keys will become
  property names and values will be converted to their equivalent data store type.
  --Returns--
  saved identity model object
  """
  new_identity = models.Identity(email=email_address,user=)

def get_identity(email_address):
  """
  --Description--
  Get an identity from the store. If given a list return a list of matching identities.
  Raise an identity does not exists exception if an email address is passed that does not exist.
  """
  pass
  
# ==============
# = Exceptions =
# ==============
class IdentityDoesNotExist(Exception):
  """
  --Description--
  Raised when an action is attempted on an identity that does not exist.
  """
  def __init__(self,value):
    self.value = value
  
  def __str__(self):
    return repr(self.value)

class AddressAlreadyUsed(Exception):
  """
  --Description--
  Raised when an attempt is made to create an identity with an email address that is already is use.
  """
  def __init__(self,value):
    self.value = value

  def __str__(self):
    return repr(self.value)