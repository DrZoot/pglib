"""
models.py
PGUserManager

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

Models for PGUserManager
"""
from google.appengine.ext import db

class Identity (db.Expando):
  """
  --Description--
  Stores a users information and mapping to a user object. Also used to represent users as datastore objects.
  Also stores arbitrary user information.
  On delete is responsible for cleaning up related 
  --Properties--
  User : UserProperty : A user object.
  """
  user = db.UserProperty(required=True)
  email = db.StringProperty(required=True)
  active = db.BooleanProperty(default=True)
  
  def delete(self):
    """
    --Description--
    Overrides the model delete method to include any membership bindings or permission bindings that reference this identity in the delete.
    """
    # Delete Permission Bindings
    db.delete(self.permissionbinding_set)
    # Delete Group Bindings
    db.delete(self.membershipbinding_set)
    super(Identity, self).delete()
    
  def get_group_permissions(self):
    """
    --Description--
    Return a list of permissions which this identity has through its group memberships.
    """
    permissions = []
    for membership_binding in self.membershipbinding_set:
      bound_group = membership_binding.group
      for permission_binding in bound_group.permissionbinding_set:
        bound_permission = permission_binding.permission
        permissions.append(bound_permission)
    return list(set(permissions))
    
  def get_all_permissions(self):
    """
    Return a list of permissions this user has both through group and user permissions.
    """
    permissions = self.get_group_permissions()
    for permission_binding in self.permissionbinding_set:
      permissions.append(permission_binding.permission)
    return list(set(permissions))
    
  def has_perm(self,perm):
    """
    Return true if the user has the specified permission. 
    Can be specified as a permission name (string) or the key of a permission (key). 
    Cannot be specified as a stringified permission key.
    If the user is inactive this always returns false
    """
    if isinstance(perm,basestring):
      perm = Permission.all.filter('name',perm).get()
    if not perm:
      # raise no such permission (perm_name)
      pass
    if not isinstance(perm,db.Model):
      #raise must pass name or object (perm)
      pass
    have_it = PermissionBinding.all.filter('permission',perm).filter('subject',self).get()
    if not have_it:
      return False
    return True
    
  def has_perms(self,perm_list):
    """
    Returns true if the user has all of the specified permissions. Permissions in the list can be specified as per has_perm.
    """
    for perm in perm_list:
      if not self.has_perm(perm):
        return False
    return True
  
class Group (db.Model):
  """
  --Description--
  Stores a group.
  --Properties--
  Name : StringProperty : The name of the group, must be unique, cannot be administrators, users.
  Description : TextProperty : Optional group description.
  """
  name = db.StringProperty(required=True)
  description = db.TextProperty(default="")
  
  def delete(self):
    """
    --Description--
    Override the model delete method to remove any memebers of this group before it is deleted.
    """
    # Delete Membership Bindings
    db.delete(self.membershipbinding_set)
    super(Group, self).delete()
  
class Permission (db.Model):
  """
  --Description--
  Stores a permission. (A permission is just a text key, your either associated or your not).
  --Properties--
  Name : StringProperty : The name of the property, must be unique.
  Description : TextProperty : Optional property description.
  """
  name = db.StringProperty(required=True)
  description = db.TextProperty(default="")
  
  def delete(self):
    """
    --Description--
    Override model delete method to remove all permission bindings when a permission is deleted.
    """
    # Delete all permission bindings
    db.delete(self.permissionbinding_set)
    super(Permission, self).delete()

class PermissionBinding (db.Model):
  """
  --Description--
  Represents relationships between permissions and groups / users.
  --Properties--
  Permission : ReferenceProperty(Permission) : A reference to the permission being bound.
  Subject : ReferenceProperty : A reference to the item being bound to the permission. Must be either a group or an identity.
  """
  permission = db.ReferenceProperty(reference_class=Permission,required=True)
  subject = db.ReferenceProperty(required=True)

class MembershipBinding (db.Model):
  """
  --Description--
  Object for storing user group membership.
  --Properties--
  Identity : ReferenceProperty : The user identity to be bound.
  Group : ReferenceProperty : The group to be bound.
  """
  identity = db.ReferenceProperty(required=True,reference_class=Identity)
  group = db.ReferenceProperty(required=True,reference_class=Group)
