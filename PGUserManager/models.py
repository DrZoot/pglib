"""
models.py
PGUserManager

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

Models for PGUserManager
"""
from google.appengine.ext import db
from utils import prefetch_refprops
import exceptions

class Identity (db.Expando):
  """
  --Description--
  Stores a users information and mapping to a user object. Also used to represent users as datastore objects.
  Also stores arbitrary user information.
  On delete is responsible for cleaning up related 
  --Properties--
  User : UserProperty : A user object.
  """
  # user = db.UserProperty()
  # TODO: email should be read only after the object is created as there is no good way to make sure it is unique on subsequent puts
  email = db.StringProperty(required=True)
  active = db.BooleanProperty(default=True)
    
  def delete(self):
    """
    Overrides the model delete method to include any membership bindings or permission bindings that reference this identity in the delete.
    """
    # Delete Permission Bindings
    db.delete([key for key in PermissionBinding.all(keys_only=True).filter('subject',self)])
    # Delete Group Bindings
    db.delete([key for key in MembershipBinding.all(keys_only=True).filter('identity',self)])
    super(Identity, self).delete()
    
  def get_group_permissions(self):
    """
    --Description--
    Return a list of permissions which this identity has through its group memberships.
    """
    group_keys = [membership_binding.group_key() for membership_binding in MembershipBinding.all().filter('identity',self)]
    permissions = list(set(db.get([permission_binding.permission_key() for permission_binding in PermissionBinding.all().filter('subject IN',group_keys)])))
    return permissions
    
  def get_all_permissions(self):
    """
    Return a list of permissions this user has both through group and user permissions.
    """
    permissions = self.get_group_permissions()
    direct_permission_keys = [permission_binding.permission_key() for permission_binding in self.permission_bindings]
    permissions = permissions + db.get(direct_permission_keys)
    return list(set(permissions))
    
  def has_permission(self,permission):
    """
    Return true if the user has the specified permission. 
    Can be specified as a permission name (string) or the key of a permission (key). 
    Cannot be specified as a stringified permission key.
    If the user is inactive this always returns false
    ident_perm_list is a PRIVATE PARAMETER it shouldnt be called outside of the model class.
    """
    if not isinstance(permission,Permission) or not isinstance(permission,db.Key):
      raise Exception('Must pass model or key')
    if isinstance(permission,db.Key):
      permission = Permission.get(permission)
    current_permissions = self.get_all_permissions()
    if permission in current_permissions:
      return True
    else:
      return False
    
  def has_permissions(self,permission_list):
    """
    Returns true if the user has all of the specified permissions. Permissions in the list can be specified as per has_permission.
    """
    for i,permission in zip(range(len(permission_list)),permission_list):
      if not isinstance(permission,Permission) or not isinstance(permission,db.Key):
        raise Exception('Must pass model or key')
      if isinstance(permission,db.Key):
        permission_list[i] = Permission.get(permission)
    permission_set = set(permission_list)
    current_permissions = set(self.get_all_permissions())
    return permission_set.issubset(current_permissions)
    

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
    db.delete([key for key in PermissionBinding.all(keys_only=True).filter('subject',self)])
    # Delete Membership Bindings
    db.delete([key for key in MembershipBinding.all(keys_only=True).filter('group',self)])
    super(Group, self).delete()
    
  def get_all_permissions(self):
    """
    Return a list of permissions this user has both through group and user permissions.
    """
    all_permission_binding_objects = [permission_binding for permission_binding in self.permission_bindings]
    all_permission_keys = [permission_binding.permission_key() for permission_binding in all_permission_binding_objects]
    permissions = db.get(all_permission_keys)
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
      raise Exception('Permission does not exist')
    if not isinstance(perm,db.Model):
      raise Exception('Method requires valid name or permission object ')
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
    """Return a list of identities attached to this group.
    """
    identities = db.get([membership_binding.identity_key() for membership_binding in self.identity_bindings])
    return list(set(identities))
    
  def has_member(self,ident):
    """Return true if the given identity is part of this group"""
    query = self.identity_bindings.filter('identity',ident)
    if query.get():
      return True
    else:
      return False
    
  def has_members(self,identities):
    """Return true if all of the given identities are part of this group"""
    current_identity_keys = [membership_binding.identity_key() for membership_binding in self.identity_bindings]
    current_identities = db.get(identity_keys)
    
  
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
    """Override model delete method to remove all permission bindings when a permission is deleted."""
    # Delete all permission bindings
    db.delete([key for key in PermissionBinding.all(keys_only=True).filter('permission',self)])
    super(Permission, self).delete()
    
  def associated_with(self,subject_key):
    if isinstance(subject_key,db.Key):
      subject = Identity.get(subject_key) or Group.get(subject_key)
    else:
      raise Exception('Must pass a key of type db.Key')
    query = self.owner_bindings.filter('subject',subject)
    if query.get():
      return True
    else:
      return False

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
  
  def get_key(self,prop_name):
    """return the key for a reference property without performing a datastore lookup"""
    return getattr(self.__class__, prop_name).get_value_for_datastore(self)
    
  def permission_key(self):
    """shortcut method to get the key of the referenced permission"""
    return self.get_key('permission')
    
  def subject_key(self):
    """shortcut method to get the key of the referenced subject"""
    return self.get_key('subject')

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
  
  def get_key(self,prop_name):
    """return the key for a reference property without performing a datastore lookup"""
    return getattr(self.__class__, prop_name).get_value_for_datastore(self)
    
  def identity_key(self):
    """return the key for the referenced identity"""
    return self.get_key('identity')
    
  def group_key(self):
    """return the key for the referenced group"""
    return self.get_key('group') 
