"""
identity.py

Created by Paul Gower on 11/23/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating identities
"""

"""
http://stackoverflow.com/questions/1054868/recursive-delete-in-google-app-engine

You need to implement this manually, by looking up affected records and deleting them at the same time as you delete the parent record. You can simplify this, if you wish, by overriding the .delete() method on your parent class to automatically delete all related records.

For performance reasons, you almost certainly want to use key-only queries (allowing you to get the keys of entities to be deleted without having to fetch and decode the actual entities), and batch deletes. For example:

db.delete(Bottom.all(keys_only=True).filter("daddy =", top).fetch(1000))
"""


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
  IdentityShim : An identity shim which represents the given datastore identity.
  """
  pass

def modify_identity(identity_shim):
  """
  --Description--
  Given an identity shim update the identity with the key stored in the shim. If the identity no longer exists
  then raise an IdentityDoesNotExist exception.
  TODO: maybe use some sort of tracking sequential hash to keep track of wether an identity has been updated since the shim was created.
  --Arguments--
  identity_shim : IdentityShim : The identity shim with updated values that we want to update.
  --Returns--
  IdentityShim : An updated version of the identity shim.
  """
  pass

def delete_identity(email_address):
  """
  --Description--
  Given a users email address delete the associated identity and all of its bindings. If passed an email address 
  that has no associated identity then raises an IdentityDoesNotExist error.
  --Arguments--
  email_address : string : An email address.
  --Returns--
  Nothing
  """
  pass
  
def identity_exists(email_address):
  """
  --Description--
  Given an email address return true if an equivalent identity exists or false if not.
  --Arguments--
  email_address : string : An email address.
  --Returns--
  True / False
  """
  pass
  
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

class IdentityShim(object):
  """
  --Description--
  Represents a datastore Identity. Passed to calling functions instead of the actual datastore object.
  Prevents people modifying and saving identity objects directly. Contains two dictonaries that are used to 
  maintain the current state of the object, currentProps and modifiedProps. currentProps contains a dictionary of
  values as stored by the Identity object, it is immutable and cannot be changed. modifiedProps is empty on
  creation but is updated as properties are changed by the user. When a property is requested by the user 
  __getattr__ does a lookup and returns either the modified property or the original.
  """
  def __init__(self,email_address,identity_key,properties=None):
    """
    --Description--
    Init for the IdentityShim.
    --Arguments--
    email_address : String : The email address associated with this identity.
    identity_key : Key : The identity key for this user.
    properties : dict : The extra properties associated with this identity.
    """
    self._email_address = email_address
    self._key = identity_key
    if not properties:
      self._currentProps = {}
    else:
      self._currentProps = properties
    self._modifiedProps = {}

  def __getattr__(self,name):
    pass

  def __setattr__(self,name,value):
    pass

  def __delattr__(self,name):
    pass