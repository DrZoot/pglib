"""
exceptions.py

Created by Paul Gower on 11/25/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Exceptions for the PGUserManager module.
"""

class IdentityDoesNotExist(Exception):
  """
  --Description--
  Raised when an action is attempted on an identity that does not exist.
  """
  def __init__(self,value):
    self.value = value
  
  def __str__(self):
    return "Identity email addresses must be unique:" + repr(self.value)

class AddressAlreadyUsed(Exception):
  """
  --Description--
  Raised when an attempt is made to create an identity with an email address that is already is use.
  """
  def __init__(self,value):
    self.value = value

  def __str__(self):
    return "Identity email addresses must be unique:" + repr(self.value)