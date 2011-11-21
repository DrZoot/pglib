# Basic util functions that I might need.

from google.appengine.ext import db

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