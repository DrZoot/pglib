"""
group.py

Created by Paul Gower on 11/23/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Functions for manipulating groups
"""
import models
import exceptions
import utils

def create_group(name,description=None):
  """create a group with the given name, if a group with the same name exists raise """
  uniqueness_query = models.Group.all(keys_only=True).filter('name',name)
  if uniqueness_query.get():
    raise exceptions.DuplicateValue(name)
  else:
    key = models.Group(key_name=name,name=name,description=description).put()
    return models.Group.get(key)
  
def get_group(name):
  """return the group with the given name or none"""
  return models.Group.all().filter('name',name).get()
  
def group_query(*args,**kwargs):
  """return a query for groups"""
  return models.Group.all(*args,**kwargs)
  
def add_member(group,identity):
  """add an identity to a group"""
  group = utils.verify_arg(group,models.Group)
  identity = utils.verify_arg(identity,models.Identity)
  membership_binding_name = identity.email + "_" + group.name
  if models.MembershipBinding.get_by_key_name(membership_binding_name):
    raise exception.BindingExists('MembershipBinding already exists')
  else:
    key = models.MembershipBinding(key_name=membership_binding_name,group=group,identity=identity).put()
    return models.MembershipBinding.get(key)
  
def remove_member(group,identity):
  """remove an identity from a group"""
  group = utils.verify_arg(group,models.Group)
  identity = utils.verify(identity,models.Identity)
  membership_binding_name = identity.email + "_" + group.name
  binding = models.MembershipBinding.get_by_key_name(membership_binding_name)
  if binding:
    binding.delete()
    # if we found a binding and deleted it return true
    return True
  else:
     # if we did not find a binding return None, no exception because the bindings are in the state expected
    return None