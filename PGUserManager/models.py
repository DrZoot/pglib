"""
models.py
PGUserManager

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

Models for PGUserManager
"""
from google.appengine.ext import db
import utils
import exceptions
import logging

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
    # TODO: compare this with using the Group.get_all_permissions method on each group and list(set([])) the result
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
    """Return true if the user has the specified permission."""
    permission = utils.verify_arg(permission,Permission)
    permission_key_name = permission.key().name()
    binding_key_name = permission_key_name + '_' + self.key().name()
    return PermissionBinding.get_by_key_name(binding_key_name)
    
  def has_permissions(self,permission_list):
    """
    Returns true if the user has all of the specified permissions. Permissions in the list can be specified as per has_permission.
    """
    if permission_list == []:
      return False
    for i,permission in zip(range(len(permission_list)),permission_list):
      permission_list[i] = utils.verify_arg(permission,Permission)
    permission_set = frozenset(permission_list)
    current_permissions = frozenset(self.get_all_permissions())
    return permission_set.issubset(current_permissions)
    
  def __hash__(self):
    """Return a hash for this model instance"""
    static_prop_values = frozenset([getattr(self,pv) for pv in ['email','active']])
    dynamic_prop_values = frozenset([getattr(self,pv) for pv in self.dynamic_properties()])
    key = str(self.key())
    return hash((static_prop_values,dynamic_prop_values,key))
    
  def __eq__(self,other):
    """equality for models"""
    if hash(self) == hash(other):
      return True
    else:
      return False
      
  def __ne__(self,other):
    """inequality for models"""
    if hash(self) != hash(other):
      return True
    else:
      return False
      
  def __repr__(self):
    """return a python representation of the model"""
    # TODO: rewrite this to deal with dynamic properties
    return 'Identity(key_name='+str(self.key().name())+' email='+str(self.email)+' active='+str(self.active)+')'
    
  def __str__(self):
    """return a string descripton for this instance"""
    return 'Identity: ' + str(self.email)

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
    return db.get([permission_binding.permission_key() for permission_binding in self.permission_bindings])

  def has_permission(self,permission):
    """
    Return true if the user has the specified permission. 
    Can be specified as a permission name (string) or the key of a permission (key). 
    Cannot be specified as a stringified permission key.
    If the user is inactive this always returns false
    ident_perm_list is a PRIVATE PARAMETER it shouldnt be called outside of the model class.
    """
    if PermissionBinding.all(keys_only=True).filter('subject',self).filter('permission',permission).get():
      return True
    else:
      return False

  def has_permissions(self,permission_list):
    """
    Returns true if the user has all of the specified permissions. Permissions in the list can be specified as per has_perm.
    """
    if permission_list == []:
      return False
    for i,permission in zip(range(len(permission_list)),permission_list):
      permission_list[i] = utils.verify_arg(permission,Permission)
    current_permissions = frozenset(self.get_all_permissions())
    return frozenset(permission_list).issubset(current_permissions)
    
  def get_all_members(self):
    """Return a list of identities attached to this group.
    """
    return db.get([membership_binding.identity_key() for membership_binding in self.identity_bindings])
    
  def has_member(self,identity):
    """Return true if the given identity is part of this group"""
    if MembershipBinding.all(keys_only=True).filter('group',self).filter('identity',identity).get():
      return True
    else:
      return False
    
  def has_members(self,identity_list):
    """Return true if all of the given identities are part of this group"""
    if identity_list == []:
      return False
    for i,identity in zip(range(len(identity_list)),identity_list):
      identity_list[i] = utils.verify_arg(identity,Identity)
    current_members = frozenset(self.get_all_members())
    return frozenset(identity_list).issubset(current_members)
    
  def __hash__(self):
    """Return a hash for this model instance"""
    static_prop_values = frozenset([getattr(self,pv) for pv in ['name','description']])
    key = str(self.key())
    return hash((static_prop_values,key))
    
  def __eq__(self,other):
    """equality for models"""
    if hash(self) == hash(other):
      return True
    else:
      return False

  def __ne__(self,other):
    """inequality for models"""
    if hash(self) != hash(other):
      return True
    else:
      return False
      
  def __repr__(self):
    """return a string representation for this instance"""
    return 'Group(key_name='+str(self.key().name())+' name='+str(self.name)+' description='+str(self.description)+')'
    
  def __str__(self):
    """return a description for this instance"""
    return 'Group: ' + str(self.name)
          
  
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
    
  def associated_with(self,subject):
    subject = utils.verify_arg(subject,Identity,Group)
    query = self.owner_bindings.filter('subject',subject)
    if query.get():
      return True
    else:
      return False
      
  def __hash__(self):
    """Return a hash for this model instance"""
    static_prop_values = frozenset([getattr(self,pv) for pv in ['name','description']])
    key = str(self.key())
    return hash((static_prop_values,key))
    
  def __eq__(self,other):
    """equality for models"""
    if hash(self) == hash(other):
      return True
    else:
      return False

  def __ne__(self,other):
    """inequality for models"""
    if hash(self) != hash(other):
      return True
    else:
      return False
      
  def __repr__(self):
    """return a rerpresentation for this model"""
    return 'Permission(key_name='+str(self.key().name())+' name='+str(self.name)+' description='+str(self.description)+')'
    
  def __str__(self):
    """return a description for this permission"""
    return 'Permission: ' + str(self.name)
      
class BindingModel(db.Model):
  """Base class to represent bindings between objects"""
  
  def get_key(self,prop_name):
    """return the key for a reference property without performing a datastore lookup"""
    return getattr(self.__class__, prop_name).get_value_for_datastore(self)
    
  def __eq__(self,other):
    """equality for models"""
    if hash(self) == hash(other):
      return True
    else:
      return False

  def __ne__(self,other):
    """inequality for models"""
    if hash(self) != hash(other):
      return True
    else:
      return False

class PermissionBinding (BindingModel):
  """Represents relationships between permissions and groups / users."""
  permission = db.ReferenceProperty(reference_class=Permission,required=True,collection_name='owner_bindings')
  subject = db.ReferenceProperty(required=True,collection_name='permission_bindings')
    
  def permission_key(self):
    """shortcut method to get the key of the referenced permission"""
    return self.get_key('permission')
    
  def subject_key(self):
    """shortcut method to get the key of the referenced subject"""
    return self.get_key('subject')
    
  def __hash__(self):
    """Return a hash for this model instance"""
    return hash((str(self.permission_key()),str(self.subject_key())))
    
  def __repr__(self):
    """returns a representation for this model"""
    return 'PermissionBinding(key_name='+str(self.key().name())+' permission='+str(self.permission_key())+' subject='+str(self.subject_key())+')'
    
  def __str__(self):
    """return a description for this model"""
    return 'PermissionBinding: '+str(self.key().name()).replace('_',' <=> ')

class MembershipBinding (BindingModel):
  """Object for storing user group membership."""
  identity = db.ReferenceProperty(required=True,reference_class=Identity,collection_name='group_bindings')
  group = db.ReferenceProperty(required=True,reference_class=Group,collection_name='identity_bindings')
    
  def identity_key(self):
    """return the key for the referenced identity"""
    return self.get_key('identity')
    
  def group_key(self):
    """return the key for the referenced group"""
    return self.get_key('group') 
    
  def __hash__(self):
    """Return a hash for this model instance"""
    return hash((str(self.identity_key()),str(self.group_key())))
    
  def __repr__(self):
    """return a representation for this model"""
    return 'MembershipBinding(key_name='+str(self.key().name())+' identity='+str(self.identity_key())+' group='+str(self.group_key())+')'
    
  def __str__(self):
    """return a description for this model instance"""
    return 'MembershipBinding: '+str(self.key().name()).replace('_',' <=> ')