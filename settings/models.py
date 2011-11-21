from google.appengine.ext import db

class Setting (db.Expando):
  """
  Holds a setting
  """
  index = db.StringProperty(required=True, indexed=True)
  owner = db.UserProperty(auto_current_user_add=True)
  is_global = db.BooleanProperty(required=True, default=False)
  # value is the expando property here
  
