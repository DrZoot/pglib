import unittest
from PGUserManager import identity
from PGUserManager import group
from PGUserManager import permission
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db
import logging

class FunctionTesting(unittest.TestCase):
  
  def testCreateIdentity(self):
    # creating an identity should return an identity object with the given email
    i = identity.create_identity('user1@example.org')
    self.assert_(isinstance(i,models.Identity),'Must return an identity object')
    
  def testCreateDuplicateIdentity(self):
    # creating a duplicate identity should result in raising a DuplicateValue
    i = identity.create_identity('user1@example.org')
    def create_duplicate_ident():
      return identity.create_identity('user1@example.org')
    self.assertRaises(exceptions.DuplicateValue, create_duplicate_ident)
    
  def testRetrieveIdentityByEmail(self):
    # retrieving an identity from the data store by email
    i = identity.create_identity('user1@example.org')
    j = identity.get_identity('user1@example.org')
    self.assert_(isinstance(j,models.Identity), 'Must return an identity object')
    self.assert_(j.email == 'user1@example.org', 'Returned identity not equal to provided email')
    
  def testRetrieveNonIdentityByEmail(self):
    # attempt to retrieve an identity that doesnt exist by email
    self.assert_(identity.get_identity('user2@example.org') == None, 'Trying to retrieve a non-existant identity must return None')
  
  def testSavingExtraProperties(self):
    # save extra properties to an existing identity
    i = identity.create_identity('user1@example.org')
    i.int_prop = 47324
    i.float_prop = 142.86323
    i.bool_prop = False
    i.string_prop = 'A testing string'
    self.assert_(isinstance(i.put(),db.Key), 'Saving the identity with properties must return a key')
    
  def testRetrievingExtraProperties(self):
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
    
  def testCreateIdentityQuery(self):
    # generate an identity query
    self.assert_(isinstance(identity.identity_query(),db.Query), 'identity.identity_query must return db.Query type')
    
  def testRetrieveIdentityUsingExpandoPropertyQuery(self):
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
    
  def testDeleteIdentity(self):
    # delete an identity
    i = identity.create_identity('user1@example.org')
    i.delete()
    self.assert_(identity.get_identity('user1@example.org') == None, 'Deleted identity should not exist in the datastore')
    
class InstanceMethodTesting(unittest.TestCase):
  
  def setUp(self):
    for g in range(10):
      group.create_group('Group'+str(g))
    for p in range(10):
      permission.create_permission('Permission'+str(p))
    i = identity.create_identity('user1@example.org')
    g = group.group_query().get()
    p_one = [p for p in permission.permission_query().order('name').fetch(5)]
    p_two = [p for p in permission.permission_query().order('name').fetch(5,offset=5)]
    group.add_member(g,i)
    for p in p_one:
      permission.bind_permission(p,i)
    for p in p_two:
      permission.bind_permission(p,g)
      
  def testGetGroupPermissions(self):
    # using the instance methods retrieve the group permissions for this id
    i = identity.get_identity('user1@example.org')
    p_two = [p for p in permission.permission_query().order('name').fetch(5,offset=5)]
    self.assert_(set(p_two) == set(i.get_group_permissions()), 'Bound permissions must equal returned permissions')
    self.assertEqual(5, len(i.get_group_permissions()), 'Number of returned permissions must equal number of bound permissions (5)')
    
  def testGetAllPermissions(self):
    # using instance method return all permissions applicable to this identity
    i = identity.get_identity('user1@example.org')
    p_all = [p for p in permission.permission_query()]
    self.assert_(set(p_all) == set(i.get_all_permissions()), 'Bound permissions must equal returned permissions')
    self.assertEqual(10, len(i.get_all_permissions()), 'Number of returned permissions must equal number of bound permissions (10)')
    
  def testHasPermission(self):
    # test that has_permission returns true for all permissions
    i = identity.get_identity('user1@example.org')
    for a in ['Permission0','Permission1','Permission2','Permission3','Permission4']:
      p = permission.get_permission(a)
      self.assert_(i.has_permission(p), 'Identity must have all passed permissions')
    p_invalid = []
    for p in range(10):
      p_invalid.append(permission.create_permission('InvalidPermission'+str(p)))
    for p in p_invalid:
      self.assert_(not i.has_permission(p), 'Identity must not have any permissions that are not bound to it')
      
class IdentityHasPermissions(unittest.TestCase):
  
  def setUp(self):
    for g in range(10):
      group.create_group('Group'+str(g))
    for p in range(10):
      permission.create_permission('Permission'+str(p))
    i = identity.create_identity('user1@example.org')
    g = group.group_query().get()
    p_one = [p for p in permission.permission_query().order('name').fetch(5)]
    p_two = [p for p in permission.permission_query().order('name').fetch(5,offset=5)]
    group.add_member(g,i)
    for p in p_one:
      permission.bind_permission(p,i)
    for p in p_two:
      permission.bind_permission(p,g)
  
  def testHasPermissionsValidInput(self):
    # identity.has_permissions should return true for any combination of valid permissions
    i = identity.get_identity('user1@example.org')
    p_all = []
    for p in permission.permission_query():
      p_all.append(p)
    for j in range(1,10):
      self.assert_(i.has_permissions(p_all[0:j]), 'Identity should return true to any combination of valid permissions')
    
  def testHasPermissionsInvalidInput(self):
    # identity.has_permissions should return true for any combination of valid permissions
    i = identity.get_identity('user1@example.org')
    p_invalid = []
    for p in range(10):
      p_invalid.append(permission.create_permission('InvalidPermission'+str(p)))
    for j in range(1,10):
      self.assert_(not i.has_permissions(p_invalid[0:j]), 'Identity should return false to any combination of invalid permissions')
      
  def testHasPermissionsEmptyInput(self):
    # identity.has_permissions should return false for an empty input list 
    i = identity.get_identity('user1@example.org')
    self.assert_(not i.has_permissions([]), 'Identity should return false for has_permissions when given an empty list')
    
  def testInvalidArgumentTypes(self):
    # ensure that when given non-permission objects a typeerror exception is raised
    i = identity.get_identity('user1@example.org')
    def invalid_args(self):
      i.has_permissions([1,'a'])
    self.assertRaises(TypeError, invalid_args)
      
    
    