"""
utils.py

Created by Paul Gower on 11/26/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Miscellaneous functions to help with various actions.
"""
from google.appengine.ext import db

def prefetch_refprops(entities, *props):
  """
  Given a list of entities, and 1 or more reference properties, prefetch the entities that the properties reference.
  Return the list of entities once the dereferenced properties have been assigned.
  """
  fields = [(entity, prop) for entity in entities for prop in props]
  ref_keys = [prop.get_value_for_datastore(x) for x, prop in fields]
  ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
  for (entity, prop), ref_key in zip(fields, ref_keys):
    prop.__set__(entity, ref_entities[ref_key])
  return entities
  
def verify_arg(arg,*args):
  """given an input argument and a list of models make sure that the input is one of the model types"""
  if isinstance(arg,db.Key):
    arg = db.get(arg)
  if isinstance(arg,tuple(*args)):
    return arg
  else:
    raise TypeError('arg must be one of:' + repr(*args))
  