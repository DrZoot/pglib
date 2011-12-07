# Basic util functions that I might need.

from google.appengine.ext import db
from constants import MAX_FETCH_LIMIT

# Credit to Trent Mick on http://code.activestate.com/recipes/115417-subset-of-a-dictionary/
def extract(d, keys):
  # extract a subset of keys from a dictionary and return a new dictionary
  return dict((k, d[k]) for k in keys if k in d)
  
def expando_prop_dict(m):
  # return a dictionary of dynamic properties from the given Expando dict
  if isinstance(m,db.Expando):
    props = {}
    for i in m.dynamic_properties():
      props[i] = getattr(m,i)
    return props
  else:
    return {}
    
def update_expando(model,dictionary):
  # update or create properties on an expando model
  for k in dictionary.keys():
    setattr(model,k,dictionary[k])
  return model
  
def fetch_all(query):
  # fetch all of the results for the given query
  offset = 0
  results = []
  query_results = query.fetch(MAX_FETCH_LIMIT,offset)
  while len(query_results) > 0:
    results.extend(query_results)
    offset = offset + MAX_FETCH_LIMIT
    query_results = query.fetch(MAX_FETCH_LIMIT,offset)
  return results

# Memcache dependancy functions.
# Tracks which stored memcache keys rely on other keys, this way when deleting or adding data we know which memcache data will be stale
# TODO: finish thus
def add_dependants(memcache_key_name,dependant_keys):
  """Update the memcache dependency sets of the given objects"""
  for dependant_key in dependant_keys:
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

# take a list of objects and return a keyname which is the concatenation of those objects with spaces removed
def key_name(*args):
  args = [str(a) for a in args]
  name = "".join(args)
  return name.lower().replace(' ','')
  
def key_to_object(key):
  # if its a key return the object, if its not a key just pass the object back
  if isinstance(key,db.Key):
    return db.get(key)
  else:
    return key
    
def object_to_key(obj):
  # if the object has a key value return it, or return the object
  if isinstance(obj,db.Key):
    return obj
  if hasattr(obj,'key'):
    return obj.key()
  raise Exception('Cant get key for Object')
  