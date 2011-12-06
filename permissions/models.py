from google.appengine.ext import db

class Permission(db.Model):
  """
  Represents both an action permission and an object permission
  """
  action = db.StringProperty(required=True)
  obj = db.ReferenceProperty()
  description = db.TextProperty() #optional
  
class PermissionBinding(db.Model):
  """
  A one-to-many binding between a permission object and another object
  """
  permission = db.ReferenceProperty(reference_class=Permission,required=True,collection_name='bound_objects')
  obj = db.ReferenceProperty(required=True,collection_name='bound_permissions')
  