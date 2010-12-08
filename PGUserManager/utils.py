"""
utils.py

Created by Paul Gower on 11/26/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Miscellaneous functions to help with various actions.
"""
from google.appengine.ext import db

def verify_arg(arg,*args):
  """given an input argument and a list of models make sure that the input is one of the model types"""
  if isinstance(arg,db.Key):
    arg = db.get(arg)
  if isinstance(arg,tuple(args)):
    return arg
  else:
    raise TypeError('arg must be one of:' + repr(*args))
  