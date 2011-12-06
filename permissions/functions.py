import models
import utils
from constants import USE_MEMCACHE
from constants import MAX_FETCH_LIMIT
from google.appengine.api import memcache
from google.appengine.api import users

PERM_KEY_NAME=lambda action,obj: "permission_to_"+str(action)+"_on_"+str(obj) if obj else "permission_to_"+str(action)
BIND_KEY_NAME=lambda perm,obj: "bind_"+str(perm)+"_to_"+str(obj)
def get_permission(action,obj=None):
  """
  Retrieve the permission specified by the name and obj
  """
  permission = memcache.get(PERM_KEY_NAME(action,obj))
  if not permission:
    permission = models.Permission.get_by_key_name(PERM_KEY_NAME(action,obj))
    if permission:
      memcache.set(PERM_KEY_NAME(action,obj),permission)
  return permission

def create_permission(action,obj=None,description=""):
  """
  Create a permission record for the given action and optional obj
  Return the created permission record
  """
  permission = models.Permission.get_or_insert(PERM_KEY_NAME(action,obj),action=action,obj=obj,description=description)
  memcache.set(PERM_KEY_NAME(action,obj),permission)
  return permission
  
# def create_permissions(*args,obj=None):
  
def delete_permission(permission):
  """
  Delete a permission record and all of its bindings / memcache records.
  """
  #TODO: put this in a transaction
  # Remove memcache objects
  memcache.delete(permission.key().name())
  # Remove bindings db objects
  bindings_keys = utils.fetch_all(models.PermissionBinding.all(keys_only=True).filter('permission =',permission))
  db.delete(bindings_keys)
  # Remove permission object itself
  permission.delete()
  
def bind_permission(permission,*args):
  """
  Bind the given permission to the objs passed in args
  Return keys for all the bindings created
  """
  bindings = []
  for obj in args:
    bindings.push(models.PermissionBinding(permission,arg).put())
    # create memcache objects
  memcache_bindings_key = permission.key().name()+"_bindings"
  existing_bindings = memcache.get(memcache_bindings_key) or []
  memcache.set(
  return bindings
  
  
def unbind_permission(permission,*args):
  """
  Remove the permission binding from the given objs
  """
  bindings_keys = utils.fetch_all(models.PermissionBinding.all(keys_only=True).filter('permission =',permission).filter('obj IN',args)
    
  
def user_has_permission(user,action,obj=None):
  """
  Does the given user have permission for the given action and optional obj?
  returns true or false
  """
  pass
  
def user_holds_permission(user,action,obj=None):
  """
  returns a list of the users/groups who hold the given permission for the given obj
  """
  pass