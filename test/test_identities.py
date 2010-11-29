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
    
  def testGetGroupPermissions(self):
    # using the instance methods retrieve the group permissions for this id
    i = identity.create_identity('user1@example.org')
    g = group.group_query().get()
    p_one = [p for p in permission.permission_query().order('name').fetch(5)]
    p_two = [p for p in permission.permission_query().order('name').fetch(5,offset=5)]
    group.add_member(g,i)
    for p in p_one:
      permission.bind_permission(p,i)
    for p in p_two:
      permission.bind_permission(p,g)
    logging.info(str([po.key().name() for po in i.get_group_permissions()]))
    logging.info(str([po.key().name() for po in p_two]))
    logging.info(str(p_two[0] == i.get_group_permissions()[0]))
    self.assert_(set(p_two) == (set(i.get_group_permissions())), 'message')
    self.assertEqual(5, len(i.get_group_permissions()), 'Number of returned permissions must equal number of bound permissions')
    
      
    
    