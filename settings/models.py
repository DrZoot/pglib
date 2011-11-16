from google.appengine.ext import db
from google.appengine.api import memcache

class Setting (db.polymodel)
  """
  Base class for a key-value settings entry
  """
  key = db.StringProperty(required=True)
  owner = db.UserProperty(auto_current_user_add=True)
  is_global = db.BoolProperty(required=True, default=False)
  
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
  
class FloatSetting(Setting)
  """
  Holds a float value
  """
  value = db.FloatProperty(required=True)  
 
  
