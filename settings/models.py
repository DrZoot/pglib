from google.appengine.ext import db
from google.appengine.api import memcache

class Setting (db.polymodel)
  """
  Base class for a key-value settings entry
  """
  key = db.StringProperty(required=True)
  
class StringSetting (Setting)
  """
  Holds a string value
  """
  value = db.StringProperty(required=True)
  
class IntSetting (Setting)
  """
  Holds an integer value
  """
  value = db.IntegerProperty(required=True)
  
class BoolSetting(Setting)
  """
  Holds a bool value
  """
  value = db.BoolProperty(required=True)
  
 
  
