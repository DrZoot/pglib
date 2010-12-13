"""
models.py

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

This file is part of PGUserManager.

PGUserManager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PGUserManager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PGUserManager.  If not, see <http://www.gnu.org/licenses/>.

Models for PGUserManager
"""
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import apiproxy_stub_map
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
    # Delete dependent memcache keys
    utils.remove_dependants([self])
    # Delete Permission Bindings
    db.delete([key for key in PermissionBinding.all(keys_only=True).filter('subject',self)])
    # Delete Group Bindings
    db.delete([key for key in MembershipBinding.all(keys_only=True).filter('identity',self)])
    super(Identity, self).delete()
    
  def get_group_permissions(self):
    """Return a list of permissions which this identity has through its group memberships."""
    cache_key = self.key().name()+'_group_permissions'
    cache_val = memcache.get(cache_key)
    if cache_val:
      return cache_val
    else:
      groups = self.get_all_groups()
      permissions = []
      for g in groups:
        permissions = permissions + g.get_all_permissions()
      deduped_permissions = list(frozenset(permissions))
      utils.add_dependants(cache_key,groups + deduped_permissions + [self])
      memcache.set(cache_key,deduped_permissions)
      return deduped_permissions
    
  def get_all_permissions(self):
    """Return a list of permissions this user has both through group and user permissions."""
    cache_key = self.key().name()+'_all_permissions'
    cache_val = memcache.get(cache_key)
    if cache_val:
      return cache_val
    else:
      groups = self.get_all_groups()
      group_permissions = self.get_group_permissions()
      direct_permissions = [binding.permission for binding in self.permission_bindings]
      deduped_permissions = list(frozenset(group_permissions + direct_permissions))
      utils.add_dependants(cache_key,groups + deduped_permissions + [self])
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
        utils.add_dependants(cache_key,[permission,self])
        memcache.set(cache_key,True)
        return True
      else:
        groups = db.get([mb.group_key() for mb in self.group_bindings])
        for group in groups:
          if group.has_permission(permission):
            utils.add_dependants(cache_key,[group,permission,self])
            memcache.set(cache_key,True)
            return True
      # dont memcache here because im not sure how you would ever get this data out, it would have no dependents
      # TODO: revist this
      return False
    
  def has_permissions(self,permission_list):
    """Returns true if the user has all of the specified permissions. Permissions in the list can be specified as per has_permission."""
    if permission_list == []:
      return False
    for i,permission in zip(range(len(permission_list)),permission_list):
      permission_list[i] = utils.verify_arg(permission,Permission)
    for permission in permission_list:
      if not self.has_permission(permission):
        return False
    return True

  def member_of_group(self,group):
    """Given a group return true if the identity is a member of it"""
    group = utils.verify_arg(group,Group)
    cache_key = self.key().name()+'_memberof_'+group.key().name()
    cache_value = memcache.get(cache_key)
    if cache_value:
      return cache_value
    else:
      binding_key_name = self.key().name() + '_' + group.key().name()
      binding = MembershipBinding.get_by_key_name(binding_key_name)
      if binding and binding.active:
        utils.add_dependants(cache_key,[group,self])
        memcache.set(cache_key,True)
        return True
      else:
        return False
    
  def member_of_groups(self,groups_list):
    """return true if the current identity belongs to all of the specified groups"""
    for i,group in zip(range(len(groups_list)),groups_list):
      groups_list[i] = utils.verify_arg(group,Group)
    for group in groups_list:
      if not self.member_of_group(group):
        return False
    return True
    
  def get_all_groups(self):
    """return a list of all groups this identity belongs to"""
    cache_key = self.key().name()+'_all_groups'
    cache_value = memcache.get(cache_key)
    if cache_value:
      return cache_value
    else:
      groups = [binding.group for binding in MembershipBinding.all().filter('identity',self)]
      utils.add_dependants(cache_key,groups + [self])
      memcache.set(cache_key,groups)
      return groups
    
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
    """Return a python representation of this Identity"""
    dynamic_property_reprs = [name + '=' + repr(getattr(self,name)) for name in self.dynamic_properties]
    dynamic_property_reprs_string = ''
    for dynamic_property_repr in dynamic_property_reprs:
      dynamic_property_reprs_string += ', ' + dynamic_property_repr
    return 'Identity(key_name='+str(self.key().name())+', email='+str(self.email)+', active='+str(self.active)+ dynamic_property_reprs_string+')'
    
  def __str__(self):
    """Return a string description of this Identity"""
    return 'Identity: ' + str(self.email)
    
  def __setattr__(self,name,value):
    """Identity Model __setattr__. Ensure that email is not changed once an Identity is created."""
    if name == 'email': raise exceptions.ReadOnlyPropertyError('The email of an identity cannot be changed after it is created.')
    super(Identity, self).__setattr__(name,value)
        
  def _update_membership_bindings(self):
    """If the active status for this binding has changed then update all of its membership bindings to reflect its new status"""
    for membership_binding in self.group_bindings:
      membership_binding.active = self.active
      membership_binding.put()

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
    utils.remove_dependants([self])
    # Delete Permission Bindings
    db.delete([key for key in PermissionBinding.all(keys_only=True).filter('subject',self)])
    # Delete Membership Bindings
    db.delete([key for key in MembershipBinding.all(keys_only=True).filter('group',self)])
    super(Group, self).delete()
    
  def get_all_permissions(self):
    """
    Return a list of permissions this group has.
    """
    cache_key = self.key().name()+'_all_permissions'
    cache_value = memcache.get(cache_key)
    if cache_value:
      return cache_value
    else:
      permissions = [permission_binding.permission for permission_binding in self.permission_bindings]
      utils.add_dependants(cache_key,permissions + [self])
      memcache.set(cache_key,permissions)
      return permissions

  def has_permission(self,permission):
    """
    Return true if the group has the specified permission. 
    """
    permission = utils.verify_arg(permission,Permission)
    cache_key = self.key().name()+'_has_'+permission.key().name()
    cache_value = memcache.get(cache_key)
    if cache_value:
      return cache_value
    else:
      permission_binding_name = permission.key().name() + "_" + self.key().name()
      if PermissionBinding.get_by_key_name(permission_binding_name):
        utils.add_dependants(cache_key,[permission,self])
        memcache.set(cache_key,True)
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
    for permission in permission_list:
      if not self.has_permission(permission):
        return False
    return True
    
  def get_all_members(self,include_inactive=False):
    """Return a list of identities attached to this group.
    """
    cache_key = self.key().name()+'_all_members_include_inactive:'+str(include_inactive)
    cache_value = memcache.get(cache_key)
    if cache_value:
      return cache_value
    else:      
      if include_inactive:
        members = [binding.identity for binding in self.identity_bindings]
      else:
        members = [binding.identity for binding in MembershipBinding.all().filter('group',self).filter('active',True)]
      utils.add_dependants(cache_key,members + [self])
      memcache.set(cache_key,members)
      return members
    
  def has_member(self,identity,include_inactive=False):
    """Return true if the given identity is part of this group"""
    cache_key = self.key().name()+'_has_member_'+identity.key().name()+'_include_inactive:'+str(include_inactive)
    cache_value = memcache.get(cache_key)
    if cache_value:
      return cache_value
    else:      
      if include_inactive:
        membership_binding = MembershipBinding.all(keys_only=True).filter('group',self).filter('identity',identity).get()
      else:
        membership_binding = MembershipBinding.all(keys_only=True).filter('group',self).filter('identity',identity).filter('active',True).get()
      if membership_binding:
        utils.add_dependants(cache_key,[identity,self])
        memcache.set(cache_key,True)
        return True
      else:
        return False
    
  def has_members(self,identity_list,include_inactive=False):
    """Return true if all of the given identities are part of this group"""
    if identity_list == []:
      return False
    for i,identity in zip(range(len(identity_list)),identity_list):
      identity_list[i] = utils.verify_arg(identity,Identity)
    for identity in identity_list:
      if not self.has_member(identity,include_inactive=include_inactive):
        return False
    return True
    
  def add_member(self, identity):
    """Add the given identity to this group"""
    identity = utils.verify_arg(identity,Identity)
    membership_binding_name = identity.key().name() + "_" + self.key().name()
    if MembershipBinding.get_by_key_name(membership_binding_name):
      raise exceptions.BindingExists('MembershipBinding already exists')
    else:
      key = MembershipBinding(key_name=membership_binding_name,group=self,identity=identity).put()
      utils.remove_dependants([identity,self])
      return MembershipBinding.get(key)
      
  def remove_member(self, identity):
    """docstring for remove_member"""
    identity = utils.verify(identity,Identity)
    membership_binding_name = identity.key().name() + "_" + self.key().name()
    binding = models.MembershipBinding.get_by_key_name(membership_binding_name)
    if binding:
      binding.delete()
      utils.remove_dependants([identity,self])
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
    return 'Group(key_name='+str(self.key().name())+', name='+str(self.name)+', description='+str(self.description)+')'
    
  def __str__(self):
    """return a description for this instance"""
    return 'Group: ' + str(self.name)
    
  def __setattr__(self,name,value):
    """Group model __setattr__. Ensure that name is not changed on Group instances."""
    if name == 'name': raise exceptions.ReadOnlyPropertyError('The name of a group cannot be changed after it is created.')
    super(Group, self).__setattr__(name,value)
          
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
    utils.remove_dependants([self])
    db.delete([key for key in PermissionBinding.all(keys_only=True).filter('permission',self)])
    super(Permission, self).delete()
    
  def permission_holders(self):
    """Return a list of all of the subjects that hold this permission (either directly or indirectly)"""
    cache_key = self.key().name()+'_holders'
    cache_value = memcache.get(cache_key)
    if cache_value:
      return cache_value
    else:
      subjects = [permission_binding.subject for permission_binding in self.owner_bindings]
      expanded_subjects = []
      for subject in subjects:
        expanded_subjects.append(subject)
        if isinstance(subject,Group):
          expanded_subjects += subject.get_all_members()
      expanded_subjects = list(set(expanded_subjects))
      utils.add_dependants(cache_key,expanded_subjects + [self])
      memcache.set(cache_key,expanded_subjects)
      return expanded_subjects
      
  def bind_to(self,subject):
    """Bind this permission to the given subject"""
    subject = utils.verify_arg(subject,Identity,Group)
    permission_binding_name = self.key().name() + "_" + subject.key().name()
    if PermissionBinding.get_by_key_name(permission_binding_name):
      raise exceptions.BindingExists("PermissionBinding already exists")
    else:
      key = PermissionBinding(key_name=permission_binding_name,permission=self,subject=subject).put()
      utils.remove_dependants([self,subject])
      return PermissionBinding.get(key)
      
  def unbind_from(self,subject):
    """Unbind this permission from the given subject"""
    subject = utils.verify_arg(subject,Identity,Group)
    permission_binding_name = self.key().name() + "_" + subject.key().name()
    binding = PermissionBinding.get_by_key_name(permission_binding_name)
    if binding:
      binding.delete()
      utils.remove_dependants([self,subject])
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
    return 'Permission(key_name='+str(self.key().name())+', name='+str(self.name)+', description='+str(self.description)+')'
    
  def __str__(self):
    """return a description for this permission"""
    return 'Permission: ' + str(self.name)
    
  def __setattr__(self,name,value):
    """Permission model __setattr__. Ensure that a permissions name is not changed."""
    if name == 'name': raise exceptions.ReadOnlyPropertyError('The name of a permission cannot be changed after it is created.')
    super(Permission,self).__setattr__(name,value)
      
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
    return 'PermissionBinding(key_name='+str(self.key().name())+', permission='+str(self.permission_key())+', subject='+str(self.subject_key())+')'
    
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
    return 'MembershipBinding(key_name='+str(self.key().name())+', identity='+str(self.identity_key())+', group='+str(self.group_key())+')'
    
  def __str__(self):
    """return a description for this model instance"""
    return 'MembershipBinding: '+str(self.key().name()).replace('_',' <=> ')
    
def pre_put_hook(service, call, request, response):
  """If an Identity is being saved update its Membership Bindings"""
  assert service == 'datastore_v3'
  if call == 'Put':
    for entity in request.entity_list():
      model_instance = db.model_from_protobuf(entity)
      if hasattr(model_instance,'_update_membership_bindings') and model_instance.is_saved():
        model_instance._update_membership_bindings()

def post_put_hook(service, call, request, response):
  """When an Entity is being saved to the Datastore invalidate all of its memcache dependants"""
  assert service == 'datastore_v3'
  if call == 'Put': 
    utils.remove_dependants([db.model_from_protobuf(entity) for entity in request.entity_list()])

apiproxy_stub_map.apiproxy.GetPreCallHooks().Append('preput', pre_put_hook, 'datastore_v3')
apiproxy_stub_map.apiproxy.GetPostCallHooks().Append('postput', post_put_hook, 'datastore_v3')
