import unittest
from PGUserManager import group
from PGUserManager import identity
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db

class FunctionTesting(unittest.TestCase):
  
  def setUp(self):
    for i in range(10):
      identity.create_identity('user' + str(i) + '@example.org')

  def testCreateGroup(self):
    # creating a group should return the created group object
    g = group.create_group('Group1')
    self.assert_(isinstance(g,models.Group), 'Create group must return an object of type Group')
    self.assert_(g.name == 'Group1', 'Returned group must be the one created')
    
  def testCreateDuplicateGroup(self):
    # creating a group with a use group name should raise a duplicatevalue error
    group.create_group('Group1')
    def create_dupe_group():
      return group.create_group('Group1')
    self.assertRaises(exceptions.DuplicateValue, create_dupe_group)
    
  def testRetrieveGroupByName(self):
    # retrieve a group from the datstore by name
    group.create_group('Group1')
    g = group.get_group('Group1')
    self.assert_(isinstance(g,models.Group), 'Must return an object of type Group')
    self.assert_(g.name == 'Group1', 'Returned group must be the one created')
    
  def testCreateGroupQuery(self):
    # create a custom query for groups
    self.assert_(isinstance(group.group_query(),db.Query), 'group.group_query must return db.Query type')
    
  def testDeleteGroup(self):
    # delete a group
    g = group.create_group('Group1')
    g.delete()
    self.assert_(group.get_group('Group1') == None, 'Deleted group should not exist on the datastore')
    
  def testAddIdentitiesToGroup(self):
    # add identities to a group
    g = group.create_group('Group1')
    identities = [ident for ident in identity.identity_query()]
    for ident in identities:
      group.add_member(g,ident)
    self.assertEqual(10, g.identity_bindings.count(), 'Number of membership bindings must equal the number of identities bound (10)')
    
  def testAddIdentitiesToMultipleGroups(self):
    # add identities to a group
    g = group.create_group('Group1')
    g2 = group.create_group('Group2')
    identities = [ident for ident in identity.identity_query()]
    for ident in identities:
      group.add_member(g,ident)
      group.add_member(g2,ident)
    self.assertEqual(10, g.identity_bindings.count(), 'Number of membership bindings must equal the number of identities bound (10)')
    self.assertEqual(10, g2.identity_bindings.count(), 'Number of membership bindings must equal the number of identities bound (10)')
    
  def testAddIdentitiesToGroupKeysOnly(self):
    # add identities to a group, use keys for the group and identities
    g_key = group.create_group('Group1').key()
    i_keys = [ik for ik in identity.identity_query(keys_only=True)]
    for ik in i_keys:
      group.add_member(g_key,ik)
    self.assertEqual(10, group.get_group('Group1').identity_bindings.count(), 'Number of membership bindings must equal the number of identities bound (10)')
    
    

