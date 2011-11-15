"""
identity.py

Created by Paul Gower on 11/23/10.
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

Functions for manipulating identities
"""
import models
import exceptions
import utils
from google.appengine.api import users
from google.appengine.api import memcache

def create_identity(email_address,active=True,klass=models.Identity,**kwargs):
  """Creates a new identity in the datstore and returns the identity object or if the email has already been used raises an DuplicateValue exception"""
  key_name = email_address.lower()
  if klass.get_by_key_name(key_name):
    raise exceptions.DuplicateValue(email_address)
  else:
    key = klass(key_name=key_name,email=email_address,active=active,**kwargs).put()
    i = klass.get(key)
    cache_key = email_address + '_identity'
    utils.add_dependants(cache_key,[i])
    memcache.set(cache_key,i)
    return i

def get_identity(email_address,include_inactive=False,klass=models.Identity):
  """Given an email address try to return a datastore object for it using the email_address as a key_name"""
  cache_key = email_address + '_identity'
  cache_value = memcache.get(cache_key)
  if cache_value: 
    if cache_value.active or (not cache_value.active and include_inactive):
      return cache_value
    else:
      return None
  else:
    i = klass.get_by_key_name(email_address.lower())
    if i:
      if i.active == True or (i.active == False and include_inactive == True):
        utils.add_dependants(cache_key,[i])
        memcache.set(cache_key,i)
        return i
    return None
  
def identity_query(klass=models.Identity,*args,**kwargs):
  """
  Equivalent to Identity.all(*args,**kwargs). Used here to shield Identity from having to be directly imported outside the module.
  """
  return klass.all(*args,**kwargs)
  
def identity_for_current_user():
  """Return the identity for the currently logged on user or None"""
  key_name = users.get_current_user().email().lower()
  return get_identity(key_name)