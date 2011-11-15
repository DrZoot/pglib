"""
utils.py

Created by Paul Gower on 11/26/10.
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

Miscellaneous functions to help with various actions.
"""
from google.appengine.ext import db
from google.appengine.api import memcache
import logging
import re
import exceptions


def verify_arg(arg,*args):
  """given an input argument and a list of models make sure that the input is one of the model types"""
  if isinstance(arg,db.Key):
    arg = db.get(arg)
  if isinstance(arg,tuple(args)):
    return arg
  else:
    raise TypeError('arg must be one of:' + str([str(type(arg)) for arg in args]))
    
def add_dependants(key,dependants):
  """Update the memcache dependency sets of the given objects"""
  for dependant in dependants:
    cache_key = str(dependant.key())+'_dependants'
    cache_value = memcache.get(cache_key)
    if cache_value:
      cache_value.add(key)
    else:
      cache_value = set([key])
    memcache.set(cache_key,cache_value)
  
def remove_dependants(dependants):
  """Remove the associated data from dependant keys"""
  for dependant in dependants:
    cache_key = str(dependant.key())+'_dependants'
    cache_value = memcache.get(cache_key)
    if cache_value:
      for dependant_key in cache_value:
        memcache.delete(dependant_key)
    memcache.delete(cache_key)
    
def validate_email_address(address):
  """Ensure that the given email address is syntactically valid"""
  # Regex is ripped from django.core.validators
  email_re = re.compile(
  r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
  r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
  r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain
  if not email_re.match(unicode(address)):
    raise exceptions.InvalidAddressFormat(address + ' is invalid')
      
