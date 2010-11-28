import unittest
from PGUserManager import identity
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db

class IdentityTestsOne(unittest.TestCase):

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
    self.assert_(identity.get_identity('user1@example.org') == None, 'Deleted object should not exist in the datastore')
    