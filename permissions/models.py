from google.appengine.ext import db

class Permission(db.Model):
  """
  Represents both an action permission and an object permission
  """
  action = db.StringProperty(required=True)
  obj = db.ReferenceProperty(required=False)
  desc = db.TextProperty(required=False) #optional
  
  def __eq__(self, other):
    if other is None:
      return False
    if self.key() == other.key():
      return True
    return False

  def __ne__(self, other):
    return not self.__eq__(other)
  
  def __str__(self):
    return "Permission to "+self.action+" on "+str(self.obj) if self.obj else "Permission to "+self.action
  
class PermissionBinding(db.Model):
  """
  A one-to-many binding between a permission object and another object
  """
  permission = db.ReferenceProperty(reference_class=Permission,required=True,collection_name='bound_objects')
  obj = db.ReferenceProperty(required=True,collection_name='bound_permissions')
  
  def __str__(self):
    return "Permission Binding: "+str(permission)+" "+str(obj)
  