"""
models.py
PGUserManager

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

Models for PGUserManager
"""
from google.appengine.ext import db
import exceptions

def validate_unique_email(email):
  """
  Given an email address ensure that it is not already used in an identity by checking that an object with the key_name does not already exist
  """
  # if Identity.get_by_key_name(email):
  #   raise exceptions.AddressAlreadyUsed(email)
  return email

class Identity (db.Expando):
  """
  --Description--
  Stores a users information and mapping to a user object. Also used to represent users as datastore objects.
  Also stores arbitrary user information.
  On delete is responsible for cleaning up related 
  --Properties--
  User : UserProperty : A user object.
  """
  user = db.UserProperty()
  email = db.StringProperty(required=True,validator=validate_unique_email)
  active = db.BooleanProperty(default=True)
    
  def delete(self):
    """
    Overrides the model delete method to include any membership bindings or permission bindings that reference this identity in the delete.
    """
    # Delete Permission Bindings
    db.delete(self.permission_bindings)
    # Delete Group Bindings
    db.delete(self.group_bindings)
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
        permissions.append(permission_binding.permission)
    return list(set(permissions))
    
  def get_all_permissions(self):
    """
    Return a list of permissions this user has both through group and user permissions.
    """
    permissions = self.get_group_permissions()
    for permission_binding in self.permissionbinding_set:
      permissions.append(permission_binding.permission)
    return list(set(permissions))
    
  def has_permission(self,perm,ident_perm_list=None):
    """
    Return true if the user has the specified permission. 
    Can be specified as a permission name (string) or the key of a permission (key). 
    Cannot be specified as a stringified permission key.
    If the user is inactive this always returns false
    ident_perm_list is a PRIVATE PARAMETER it shouldnt be called outside of the model class.
    """
    if isinstance(perm,basestring):
      perm = Permission.all.filter('name',perm).get()
    if not perm:
      # raise no such permission (perm_name)
      pass
    if not isinstance(perm,db.Model):
      #raise must pass name or object (perm)
      pass
    if not ident_perm_list:
      ident_perm_list = self.get_all_permissions()
    if perm in ident_perm_list:
      return True
    else:
      return False
    
  def has_permissions(self,perm_list):
    """
    Returns true if the user has all of the specified permissions. Permissions in the list can be specified as per has_permission.
    """
    ident_perm_list = self.get_all_permissions()
    for perm in perm_list:
      if not self.has_permission(perm,ident_perm_list=ident_perm_list):
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
    # Delete Permission Bindings
    db.delete(self.permission_bindings)
    # Delete Membership Bindings
    db.delete(self.identity_bindings)
    super(Group, self).delete()
    
  def get_all_permissions(self):
    """
    Return a list of permissions this user has both through group and user permissions.
    """
    permissions = []
    for permission_binding in self.permissionbinding_set:
      permissions.append(permission_binding.permission)
    return list(set(permissions))

  def has_permission(self,perm,ident_perm_list=None):
    """
    Return true if the user has the specified permission. 
    Can be specified as a permission name (string) or the key of a permission (key). 
    Cannot be specified as a stringified permission key.
    If the user is inactive this always returns false
    ident_perm_list is a PRIVATE PARAMETER it shouldnt be called outside of the model class.
    """
    if isinstance(perm,basestring):
      perm = Permission.all.filter('name',perm).get()
    if not perm:
      # raise no such permission (perm_name)
      pass
    if not isinstance(perm,db.Model):
      #raise must pass name or object (perm)
      pass
    if not ident_perm_list:
      ident_perm_list = self.get_all_permissions()
    if perm in ident_perm_list:
      return True
    else:
      return False

  def has_permissions(self,perm_list):
    """
    Returns true if the user has all of the specified permissions. Permissions in the list can be specified as per has_perm.
    """
    ident_perm_list = self.get_all_permissions()
    for perm in perm_list:
      if not self.has_permission(perm,ident_perm_list=ident_perm_list):
        return False
    return True
    
  def get_all_members(self):
    """
    Return a list of identities attached to this group.
    """
    members = []
    for membership_binding in self.meembershipbinding_set:
      members.append(membership_binding.identity)
    return members
    
  def has_member(self,ident):
    """Return true if the given identity is part of this group"""
    pass
    
  def has_members(self,idents):
    """Return true if all of the given identities are part of this group"""
    pass
    
  
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
    db.delete(self.owner_bindings)
    super(Permission, self).delete()

class PermissionBinding (db.Model):
  """
  --Description--
  Represents relationships between permissions and groups / users.
  --Properties--
  Permission : ReferenceProperty(Permission) : A reference to the permission being bound.
  Subject : ReferenceProperty : A reference to the item being bound to the permission. Must be either a group or an identity.
  """
  permission = db.ReferenceProperty(reference_class=Permission,required=True,collection_name='owner_bindings')
  subject = db.ReferenceProperty(required=True,collection_name='permission_bindings')

class MembershipBinding (db.Model):
  """
  --Description--
  Object for storing user group membership.
  --Properties--
  Identity : ReferenceProperty : The user identity to be bound.
  Group : ReferenceProperty : The group to be bound.
  """
  identity = db.ReferenceProperty(required=True,reference_class=Identity,collection_name='group_bindings')
  group = db.ReferenceProperty(required=True,reference_class=Group,collection_name='identity_bindings')
