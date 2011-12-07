import models
import utils
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
import logging


def get(action,obj=None):
  """
  Retrieve the permission specified by the name and obj
  """
  m = models.Permission.get_by_key_name(utils.key_name(action,obj))
  if m is None:
    m = models.Permission.all().filter('action',action).filter('obj',obj).get()
  if m is not None:
    return m
  else:
    return None
    

def create(action,obj=None,desc=""):
  """
  Create a permission record for the given action and optional obj
  Returns the permission instance that was created (NOT a key)
  """
  permission = models.Permission.get_or_insert(utils.key_name(action,obj),action=action,obj=obj,desc=desc)
  return permission
  
# def create_permissions(*args,obj=None):
  
def delete(permission):
  """
  Delete a permission record and all of its bindings / memcache records.
  """
  bindings_keys = utils.fetch_all(models.PermissionBinding.all(keys_only=True).filter('permission',permission))
  db.delete(bindings_keys)
  # Remove permission object itself
  permission.delete()
  
def bind(permission,*args):
  """
  Bind the given permission to the objs passed in args
  Return keys for all the bindings created
  """
  permission = utils.object_to_key(permission)
  args = [utils.object_to_key(arg) for arg in args]
  bindings = []
  for arg in args:
    bindings.append(models.PermissionBinding(permission=permission,obj=arg).put())
    # create memcache objects
  return bindings
  
  
def unbind(permission,*args):
  """
  Unbind the permission from the given objects, if no objects given unbind the permission from all objects (delete all bindings where permission=permission)
  Returns the number of bindings that were removed or 0
  """
  count = 0
  if len(args) == 0:
    bindings = utils.fetch_all(models.PermissionBinding.all(keys_only=True).filter('permission',permission))
    count += len(bindings)
    db.delete(bindings)
  else:
    for arg in args:
      bindings = utils.fetch_all(models.PermissionBinding.all(keys_only=True).filter('permission',permission).filter('obj',arg))
      count += len(bindings)
      db.delete(bindings)
  return count

def has_permission(obj,permission):
  # is there a binding from the obj to the permission
  logging.info(obj)
  logging.info(permission)
  binding = models.PermissionBinding.all().filter('permission',permission).filter('obj',obj).get()
  logging.info(binding)
  if binding is None:
    return False
  else:
    return True
    

  