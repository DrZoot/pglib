import unittest
from PGUserManager import group
from PGUserManager import identity
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db

class GroupTestsOne(unittest.TestCase):
  
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
    

