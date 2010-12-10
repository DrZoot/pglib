import unittest
from PGUserManager import identity
from PGUserManager import group
from PGUserManager import permission
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db
from google.appengine.api import memcache
import logging

class FunctionTesting(unittest.TestCase):
  def setUp(self):
    memcache.flush_all()
  
  def test_CreateIdentity(self):
    # creating an identity should return an identity object with the given email
    i = identity.create_identity('user1@example.org')
    self.assert_(isinstance(i,models.Identity),'Must return an identity object')
    
  def test_CreateDuplicateIdentity(self):
    # creating a duplicate identity should result in raising a DuplicateValue
    i = identity.create_identity('user1@example.org')
    def create_duplicate_ident():
      return identity.create_identity('user1@example.org')
    self.assertRaises(exceptions.DuplicateValue, create_duplicate_ident)
    
  def test_RetrieveIdentityByEmail(self):
    # retrieving an identity from the data store by email
    i = identity.create_identity('user1@example.org')
    j = identity.get_identity('user1@example.org')
    self.assert_(isinstance(j,models.Identity), 'Must return an identity object')
    self.assert_(j.email == 'user1@example.org', 'Returned identity not equal to provided email')
    
  def test_RetrieveNonIdentityByEmail(self):
    # attempt to retrieve an identity that doesnt exist by email
    self.assert_(identity.get_identity('user2@example.org') == None, 'Trying to retrieve a non-existant identity must return None')
    
  def test_RetrieveInactiveIdentity(self):
    # attempt to get an inactive identity by email
    i = identity.create_identity('user1@example.org',active=False)
    self.assert_(not identity.get_identity('user1@example.org'), 'Inactive identities must not be returned')
    
  def test_QueryInactiveIdentity(self):
    # attempt to query for an inactive identity, should return
    i = identity.create_identity('user1@example.org',active=False)
    j = identity.identity_query().filter('email','user1@example.org').get()
    self.assert_(isinstance(j,models.Identity), 'Querying for an inactive user should return the inactive user (queries ignore active status)')
    self.assert_(j.active == False, 'The queried identity should be inactive (active=False)')
  
  def test_SavingExtraProperties(self):
    # save extra properties to an existing identity
    i = identity.create_identity('user1@example.org')
    i.int_prop = 47324
    i.float_prop = 142.86323
    i.bool_prop = False
    i.string_prop = 'A testing string'
    self.assert_(isinstance(i.put(),db.Key), 'Saving the identity with properties must return a key')
    
  def test_RetrievingExtraProperties(self):
    # retrieve extra properties from an identity
    i = identity.create_identity('user1@example.org')
    i.int_prop = 47324
    i.float_prop = 142.86323
    i.bool_prop = False
    i.string_prop = 'A testing string'
    i.put()
    j = identity.get_identity('user1@example.org')
    self.assert_(j.int_prop == 47324, 'Identity int_prop must return same value (47324)')
    self.assert_(j.float_prop == 142.86323, 'Identity float_prop must return same value (142.86323)')
    self.assert_(j.bool_prop == False, 'Identity bool_prop must return same value (False)')
    self.assert_(j.string_prop == 'A testing string', 'Identity string_prop must return same value (A testing string)')
    
  def test_CreateIdentityQuery(self):
    # generate an identity query
    self.assert_(isinstance(identity.identity_query(),db.Query), 'identity.identity_query must return db.Query type')
    
  def test_RetrieveIdentityUsingExpandoPropertyQuery(self):
    # query the datastore for an identity based on a perviously added non-standard query
    i = identity.create_identity('user1@example.org')
    i.int_prop = 47324
    i.float_prop = 142.86323
    i.bool_prop = False
    i.string_prop = 'A testing string'
    i.put()
    j = identity.identity_query().filter('int_prop',47324).get()
    self.assert_(isinstance(j,models.Identity), 'Query for an optional property should return an identity object')
    self.assert_(j.int_prop == 47324, 'Returned object should match query properties')
    
  def test_DeleteIdentity(self):
    # delete an identity
    i = identity.create_identity('user1@example.org')
    i.delete()
    self.assert_(identity.get_identity('user1@example.org') == None, 'Deleted identity should not exist in the datastore')
    
class InstanceMethodTesting(unittest.TestCase):
  
  def setUp(self):
    memcache.flush_all()
    identities = [identity.create_identity(i) for i in ['user1@example.org','user2@example.org']]
    groups = [group.create_group(g) for g in ['Group1','Group2']]
    groups[0].add_member(identities[0])
    permissions_one = [permission.create_permission(p) for p in ['GroupPermission1','GroupPermission2']]
    permissions_two = [permission.create_permission(p) for p in ['IdentPermission1','IdentPermission2']]
    for p in permissions_one:
      p.bind_to(groups[0])
    for p in permissions_two:
      p.bind_to(identities[0])    
  
  def test_GetGroupPermissions(self):
    # using the instance methods retrieve the group permissions for this id
    i = identity.get_identity('user1@example.org')
    g = group.get_group('Group1')
    permissions = [permission.get_permission(p) for p in ['GroupPermission1','GroupPermission2']]
    self.assert_(set(permissions) == set(i.get_group_permissions()), 'Bound permissions must equal returned permissions')
    self.assertEqual(2, len(i.get_group_permissions()), 'Number of returned permissions must equal number of bound permissions (5)')
    
  def test_GetAllPermissions(self):
    # using instance method return all permissions applicable to this identity
    i = identity.get_identity('user1@example.org')
    permissions = [permission.get_permission(p) for p in ['GroupPermission1','GroupPermission2','IdentPermission1','IdentPermission2']]
    self.assert_(set(permissions) == set(i.get_all_permissions()), 'Bound permissions must equal returned permissions')
    self.assertEqual(4, len(i.get_all_permissions()), 'Number of returned permissions must equal number of bound permissions (8)')
    
  def test_HasPermission(self):
    # test that has_permission returns true for all permissions
    i = identity.get_identity('user1@example.org')
    permissions = [permission.get_permission(p) for p in ['GroupPermission1','GroupPermission2','IdentPermission1','IdentPermission2']]
    logging.info(permissions)
    logging.info('=================')
    logging.info(i.get_all_permissions())
    logging.info([pb for pb in models.PermissionBinding.all()])
    for p in permissions:
      logging.info(i.has_permission(p))
      self.assert_(i.has_permission(p), 'Identity must return true for all permissions it is bound to')
    invalid_permissions = [permission.create_permission(p) for p in ['InvalidPermission1','InvalidPermission2']]
    for p in invalid_permissions:
      self.assert_(not i.has_permission(p), 'Identity must not have any permissions that are not bound to it')
      
class IdentityHasPermissions(unittest.TestCase):
  
  def setUp(self):
    memcache.flush_all()
    identities = [identity.create_identity(i) for i in ['user1@example.org','user2@example.org']]
    groups = [group.create_group(g) for g in ['Group1','Group2']]
    groups[0].add_member(identities[0])
    permissions_one = [permission.create_permission(p) for p in ['GroupPermission1','GroupPermission2']]
    permissions_two = [permission.create_permission(p) for p in ['IdentPermission1','IdentPermission2']]
    for p in permissions_one:
      p.bind_to(groups[0])
    for p in permissions_two:
      p.bind_to(identities[0])
  
  def test_HasPermissionsValidInput(self):
    # identity.has_permissions should return true for any combination of valid permissions
    i = identity.get_identity('user1@example.org')
    permissions = [permission.get_permission(p) for p in ['GroupPermission1','GroupPermission2','IdentPermission1','IdentPermission2']]
    for j in range(1,10):
      self.assert_(i.has_permissions(permissions[0:j]), 'Identity should return true to any combination of valid permissions')
    
  def test_HasPermissionsInvalidInput(self):
    # identity.has_permissions should return true for any combination of valid permissions
    i = identity.get_identity('user1@example.org')
    permissions = [permission.create_permission(p) for p in ['InvalidPermission1','InvalidPermission2']]
    self.assert_(not i.has_permissions([permissions[0]]), 'Identity should return false to any combination of invalid permissions')
    self.assert_(not i.has_permissions([permissions[1]]), 'Identity should return false to any combination of invalid permissions')
    self.assert_(not i.has_permissions(permissions), 'Identity should return false to any combination of invalid permissions')
      
  def test_HasPermissionsEmptyInput(self):
    # identity.has_permissions should return false for an empty input list 
    i = identity.get_identity('user1@example.org')
    self.assert_(not i.has_permissions([]), 'Identity should return false for has_permissions when given an empty list')
    
  def test_InvalidArgumentTypes(self):
    # ensure that when given non-permission objects a typeerror exception is raised
    i = identity.get_identity('user1@example.org')
    def invalid_args(self):
      i.has_permissions([1,'a'])
    self.assertRaises(TypeError, invalid_args)
    
class ActiveIdentity(unittest.TestCase):
  def setUp(self):
    memcache.flush_all()
    
  def test_RetrieveInactiveIdentity(self):
    # Retrieving an inactive identity should return false
    i = identity.create_identity('user1@example.org',active=False)
    self.assert_(identity.get_identity('user1@example.org') == None, 'Trying to retrieve an inactive identity using get_identity should return None')
    
  def test_QueryInactiveIdentity(self):
    # Query for an inactive identity should return true
    i = identity.create_identity('user1@example.org',active=False)
    qr = identity.identity_query().filter('email','user1@example.org').get()
    self.assert_(isinstance(qr,models.Identity), 'Query for an inactive identitiy should return the identity')
    
      
    
    