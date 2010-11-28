"""
exceptions.py

Created by Paul Gower on 11/25/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Exceptions for the PGUserManager module.
"""

class RecordDoesNotExist(Exception):
  """Raised when an attempt is made to access a record that does not exist"""
  pass
  
class DuplicateValue(Exception):
  """Raised when trying to create a new value with a non-unique key (identity/permission/group)"""
  pass
    
class BindingExists(Exception):
  """Raised when trying to create a binding that already exists"""
  pass