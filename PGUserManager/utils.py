"""
utils.py

Created by Paul Gower on 11/26/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Miscellaneous functions to help with various actions.
"""
from google.appengine.ext import db
from google.appengine.api import memcache

def verify_arg(arg,*args):
  """given an input argument and a list of models make sure that the input is one of the model types"""
  if isinstance(arg,db.Key):
    arg = db.get(arg)
  if isinstance(arg,tuple(args)):
    return arg
  else:
    raise TypeError('arg must be one of:' + repr(*args))
    
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
  
def remove_dependants(subject):
  """Remove the associated data from dependant keys"""
  cache_key = str(subject.key())+'_dependants'
  cache_value = memcache.get(cache_key)
  if cache_value:
    for dependant_key in cache_value:
      memcache.delete(dependant_key)
      
      