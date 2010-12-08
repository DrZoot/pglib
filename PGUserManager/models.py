"""
models.py
PGUserManager

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

Models for PGUserManager
"""
from google.appengine.ext import db
from google.appengine.api import memcache
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
    """Overrides the model delete method to include any membership bindings or permission bindings that reference this identity in the delete."""
    # Delete dependant memcache keys
    utils.remove_dependants(self)
    # Delete Permission Bindings
    db.delete([key for key in PermissionBinding.all(keys_only=True).filter('subject',self)])
    # Delete Group Bindings
    db.delete([key for key in MembershipBinding.all(keys_only=True).filter('identity',self)])
    super(Identity, self).delete()
    
  def get_group_permissions(self):
    """Return a list of permissions which this identity has through its group memberships."""
    # TODO: compare this with using the Group.get_all_permissions method on each group and list(set([])) the result
    cache_key = self.key().name()+'_group_permissions'
    cache_val = memcache.get(cache_key)
    if cache_val:
      return cache_val
    else:
      groups = self.get_all_groups()
      utils.add_dependants(cache_key,groups)
      permissions = []
      for g in groups:
        permissions = permissions + g.get_all_permissions()
      deduped_permissions = list(frozenset(permissions))
      utils.add_dependants(cache_key,deduped_permissions)
      memcache.set(cache_key,deduped_permissions)
      return deduped_permissions
    
  def get_all_permissions(self):
    """
    Return a list of permissions this user has both through group and user permissions.
    """
    cache_key = self.key().name()+'_all_permissions'
    cache_val = memcache.get(cache_key)
    if cache_val:
      return cache_val
    else:
      groups = self.get_all_groups()
      utils.add_dependants(cache_key,groups)
      group_permissions = self.get_group_permissions()
      utils.add_dependants(cache_key,group_permissions)
      direct_permissions = [binding.permission for binding in self.permission_bindings]
      utils.add_dependants(cache_key,direct_permissions)
      deduped_permissions = list(frozenset(group_permissions + direct_permissions))
      memcache.set(cache_key,deduped_permissions)
      return deduped_permissions
    
  def has_permission(self,permission):
    """Return true if the user has the specified permission."""
    permission = utils.verify_arg(permission,Permission)
    cache_key = self.key().name()+'_has_'+permission.key().name()
    cache_value = memcache.get(cache_key)
    if cache_value:
      return cache_value
    else:      
      binding_key_name = permission.key().name() + '_' + self.key().name()
      if PermissionBinding.get_by_key_name(binding_key_name):
        utils.add_dependants(cache_key,[permission])
        memcache.set(cache_key,True)
        return True
      else:
        groups = db.get([mb.group_key() for mb in self.group_bindings])
        for group in groups:
          if group.has_permission(permission):
            utils.add_dependants(cache_key,[group,permission])
            memcache.set(cache_key,True)
            return True
      # dont memcache here because im not sure how you would ever get this data out, it would have no dependents
      return False
    
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

  def member_of_group(self,group):
    """given a group return true if the identity is a member of it"""
    group = utils.verify_arg(group,Group)
    binding_key_name = self.key().name() + '_' + group.key().name()
    binding = MembershipBinding.get_by_key_name(binding_key_name)
    if binding.active:
      return True
    else:
      return False
    
  def member_of_groups(self,groups_list):
    """return true if the current identity belongs to all of the specified groups"""
    for i,group in zip(range(len(groups_list)),groups_list):
      permission_list[i] = utils.verify_arg(group,Group)
    # TODO: should probably in its own method, get_all_groups
    all_groups = [binding.group for binding in MembershipBinding.all().filter('identity',self).filter('active',True)]
    return frozenset(groups_list).issubset(frozenset(all_groups))
    
  def get_all_groups(self):
    """return a list of all groups this identity belongs to"""
    return [binding.group for binding in MembershipBinding.all().filter('identity',self).filter('active',True)]
    
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
    
  def __setattr__(self,name,value):
    """override setting the active value and update the membership bindings at the same time"""
    if name == 'active':
      if value != self.active:
        db.Expando.__setattr__(self, name, value)
        membership_bindings = []
        for membership_binding in self.group_bindings:
          membership_binding.active = value
          membership_bindings.append(membership_binding)
        db.put(membership_bindings)
        # TODO: make sure this is mentioned in docs and remembered, could be a real performance bitch if people didnt know it was doing this
        self.put()
    else:
      db.Expando.__setattr__(self, name, value)          

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
    Override the model delete method to remove any members of this group before it is deleted.
    """
    # Delete Permission Bindings
    db.delete([key for key in PermissionBinding.all(keys_only=True).filter('subject',self)])
    # Delete Membership Bindings
    db.delete([key for key in MembershipBinding.all(keys_only=True).filter('group',self)])
    super(Group, self).delete()
    
  def get_all_permissions(self):
    """
    Return a list of permissions this group has.
    """
    # TODO: investigate more efficient ways of doing this
    return db.get([permission_binding.permission_key() for permission_binding in self.permission_bindings])

  def has_permission(self,permission):
    """
    Return true if the group has the specified permission. 
    """
    permission_binding_name = permission.key().name() + "_" + self.key().name()
    if PermissionBinding.get_by_key_name(permission_binding_name):
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
    
  def get_all_members(self,include_inactive=False):
    """Return a list of identities attached to this group.
    """
    if include_inactive:
      members = [binding.identity for binding in self.identity_bindings]
    else:
      members = [binding.identity for binding in MembershipBinding.all().filter('group',self).filter('active',True)]
    return members
    
  def has_member(self,identity,include_inactive=False):
    """Return true if the given identity is part of this group"""
    if include_inactive:
      membership_binding = MembershipBinding.all(keys_only=True).filter('group',self).filter('identity',identity).get()
      if membership_binding: return True
    else:
      membership_binding = MembershipBinding.all(keys_only=True).filter('group',self).filter('identity',identity).filter('active',True).get()
      if membership_binding: return True
    return False
    
  def has_members(self,identity_list,include_inactive=False):
    """Return true if all of the given identities are part of this group"""
    if identity_list == []:
      return False
    for i,identity in zip(range(len(identity_list)),identity_list):
      identity_list[i] = utils.verify_arg(identity,Identity)
    current_members = frozenset(self.get_all_members(include_inactive=include_inactive))
    return frozenset(identity_list).issubset(current_members)
    
  def add_member(self, identity):
    """Add the given identity to this group"""
    identity = utils.verify_arg(identity,Identity)
    membership_binding_name = identity.key().name() + "_" + self.key().name()
    if MembershipBinding.get_by_key_name(membership_binding_name):
      raise exceptions.BindingExists('MembershipBinding already exists')
    else:
      key = MembershipBinding(key_name=membership_binding_name,group=self,identity=identity).put()
      return MembershipBinding.get(key)
      
  def remove_member(self, identity):
    """docstring for remove_member"""
    identity = utils.verify(identity,Identity)
    membership_binding_name = identity.key().name() + "_" + self.key().name()
    binding = models.MembershipBinding.get_by_key_name(membership_binding_name)
    if binding:
      binding.delete()
      return True # found and deleted
    else:
      return None # not found
    
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
      
  def bind_to(self,subject):
    """Bind this permission to the given subject"""
    subject = utils.verify_arg(subject,Identity,Group)
    permission_binding_name = self.key().name() + "_" + subject.key().name()
    if PermissionBinding.get_by_key_name(permission_binding_name):
      raise exceptions.BindingExists("PermissionBinding already exists")
    else:
      key = PermissionBinding(key_name=permission_binding_name,permission=self,subject=subject).put()
      return PermissionBinding.get(key)
      
  def unbind_from(self,subject):
    """Unbind this permission from the given subject"""
    subject = utils.verify_arg(subject,Identity,Group)
    permission_binding_name = self.key().name() + "_" + subject.key().name()
    binding = PermissionBinding.get_by_key_name(permission_binding_name)
    if binding:
      binding.delete()
      return True # found and deleted
    else:
      return None # not found
    
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
  active = db.BooleanProperty(default=True)
    
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