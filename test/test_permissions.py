import unittest
from PGUserManager import group
from PGUserManager import identity
from PGUserManager import permission
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db

class FunctionTesting(unittest.TestCase):
  
  def setUp(self):
    for i in range(10):
      identity.create_identity('User' + str(i) + '@example.org')
    for g in range(5):
      group.create_group('Group' + str(g))
  
  def testCreatePermission(self):
    # create a permission object
    p = permission.create_permission('Permission1')
    self.assert_(isinstance(p,models.Permission), 'Must return an object of type models.Permission')
    
  def testCreateDuplicatePermission(self):
    # create a permission with a name thats already used
    permission.create_permission('Permission1')
    def create_dupe_permission():
      return permission.create_permission('Permission1')
    self.assertRaises(exceptions.DuplicateValue, create_dupe_permission)
    
  def testRetrieveGroupByName(self):
    # retrieve a group using a string name
    permission.create_permission('Permission1')
    p = permission.get_permission('Permission1')
    self.assert_(isinstance(p,models.Permission), 'Must return an object of type models.Permission')
    self.assert_(p.name == 'Permission1', 'Returned object must be the one queried')
    
  def testCreatePermissionQuery(self):
    # create a permission query
    self.assert_(isinstance(permission.permission_query(),db.Query), 'Must return a db.Query object')
    
  def testDeletePermission(self):
    # delete a permission from the datastore
    p = permission.create_permission('Permission1')
    p.delete()
    self.assertEqual(None, permission.get_permission('Permission1'), 'Deleted object should no longer exist in the datastore')
    
  def testBindPermissionToGroup(self):
    # bind a permission to a group
    p = permission.create_permission('Permission1')
    g = group.get_group('Group1')
    permission.bind_permission(p,g)
    pb = models.PermissionBinding.all().filter('permission',p).filter('subject',g).get()
    self.assert_(isinstance(pb,models.PermissionBinding), 'PermissionBinding must exist and be of type models.PermissionBinding')
    self.assertEqual(p.key(), pb.permission.key(), 'PermissionBinding permission key must match bound permission')
    self.assertEqual(g.key(), pb.subject.key(), 'PermissionBinding subject key must match bound group')
    self.assertEqual(g.permission_bindings.get().key(), pb.key(), 'Group permission_binding back-reference must match retrieved PermissionBinding')
    self.assertEqual(p.owner_bindings.get().key(), pb.key(), 'Permission owner_binding back-reference must match retrieved PermissionBinding')
    
  def testBindPermissionToIdentity(self):
    # bind a permission to an identity
    p = permission.create_permission('Permission1')
    i = identity.get_identity('User1@example.org')
    permission.bind_permission(p,i)
    pb = models.PermissionBinding.all().filter('permission',p).filter('subject',i).get()
    self.assert_(isinstance(pb,models.PermissionBinding), 'PermissionBinding must exist and be of type models.PermissionBinding')
    self.assertEqual(p.key(), pb.permission.key(), 'PermissionBinding permission key must match bound permission')
    self.assertEqual(i.key(), pb.subject.key(), 'PermissionBinding subject key must match bound identity')
    self.assertEqual(i.permission_bindings.get().key(), pb.key(), 'Identity permission_binding back-reference must match retrieved PermissionBinding')
    self.assertEqual(p.owner_bindings.get().key(), pb.key(), 'Permission owner_binding back-reference must match retrieved PermissionBinding')
    
class InstanceMethodTesting(unittest.TestCase):
  pass
    
    
    