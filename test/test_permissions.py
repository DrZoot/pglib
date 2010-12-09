import unittest
from PGUserManager import group
from PGUserManager import identity
from PGUserManager import permission
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db

class FunctionTesting(unittest.TestCase):
  def setUp(self):
    i = identity.create_identity('user1@example.org')
    g = group.create_group('Group1')
    permissions = [permission.create_permission(p) for p in ['Permission1','Permission2','Permission3']]
  
  def test_CreatePermission(self):
    # create a permission object
    p = permission.create_permission('Permission4')
    self.assert_(isinstance(p,models.Permission), 'Must return an object of type models.Permission')
    
  def test_CreateDuplicatePermission(self):
    # create a permission with a name thats already used
    def create_dupe_permission():
      return permission.create_permission('Permission1')
    self.assertRaises(exceptions.DuplicateValue, create_dupe_permission)
    
  def test_RetrievePermissionByName(self):
    # retrieve a permission using a string name
    p = permission.get_permission('Permission1')
    self.assert_(isinstance(p,models.Permission), 'Must return an object of type models.Permission')
    self.assert_(p.name == 'Permission1', 'Returned object must be the one queried')
    
  def test_CreatePermissionQuery(self):
    # create a permission query
    self.assert_(isinstance(permission.permission_query(),db.Query), 'Must return a db.Query object')
    
  def test_DeletePermission(self):
    # delete a permission from the datastore
    p = permission.get_permission('Permission1')
    p.delete()
    self.assertEqual(None, permission.get_permission('Permission1'), 'Deleted object should no longer exist in the datastore')
    
  def test_BindPermissionToGroup(self):
    # bind a permission to a group
    g = group.get_group('Group1')
    permissions = [permission.get_permission(p) for p in ['Permission1','Permission2','Permission3']]
    for p in permissions:
      p.bind_to(g)
    self.assert_(g.has_permissions(permissions), 'Group should return all bound permissions')
    
  def test_BindPermissionToIdentity(self):
    # bind a permission to an identity
    i = identity.get_identity('user1@example.org')
    permissions = [permission.get_permission(p) for p in ['Permission1','Permission2','Permission3']]
    for p in permissions:
      p.bind_to(i)
    self.assert_(i.has_permissions(permissions), 'Identity should return all bound permissions')
    
class InstanceMethodTesting(unittest.TestCase):
  def setUp(self):
    groups = [group.create_group(g) for g in ['Group1','Group2']]
    identities = [identity.create_identity(i) for i in ['user1@example.org','user2@example.org']]
    permissions = [permission.create_permission(p) for p in ['Permission1','Permission2']]
    permissions[0].bind_to(groups[0])
    permissions[1].bind_to(identities[0])
      
  # def test_AssociatedWith(self):
  #   # return true when passed subjects that are associated
  #   g = group.get_group('Group1')
  #   i = identity.get_identity('user1@example.org')
  #   p_g = permission.get_permission('Permission1')
  #   p_i = permission.get_permission('Permission2')
  #   self.assert_(p_g.associated_with(g), 'Should return true if bound')
  #   self.assert_(p_i.associated_with(i), 'Should return true if bound')