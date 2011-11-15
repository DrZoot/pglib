"""
exceptions.py

Created by Paul Gower on 11/25/10.
Copyright (c) 2010 Paul Gower. All rights reserved.

This file is part of PGUserManager.

PGUserManager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PGUserManager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PGUserManager.  If not, see <http://www.gnu.org/licenses/>.

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
  
class ReadOnlyPropertyError(Exception):
  """Raised when trying to set a value on a read only model property"""
  pass
  
class InvalidAddressFormat(Exception):
  """Raised when Identity is passed an email address with an invalid format"""
  pass
    