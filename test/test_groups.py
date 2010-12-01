import unittest
from PGUserManager import group
from PGUserManager import identity
from PGUserManager import permission
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db
import logging

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
    
class InstanceMethodTesting(unittest.TestCase):
  def setUp(self):
    identities = []
    for i in range(20):
      identities.append(identity.create_identity('User'+str(i)+'@example.org'))
    groups = []
    for g in range(4):
      groups.append(group.create_group('Group'+str(g)))
    permissions = []
    for p in range(40):
      permissions.append(permission.create_permission('Permission'+str(p)))
    for r in [(0,5,0),(5,10,1),(10,15,2),(15,20,3)]:
      for i in identities[r[0]:r[1]]:
        group.add_member(groups[r[2]],i)
    for r in range(20):
      permission.bind_permission(permissions[r],identities[r])
    for r in [(20,25,0),(25,30,1),(30,35,2),(35,40,3)]:
      for p in permissions[r[0]:r[1]]:
        permission.bind_permission(p,groups[r[2]])
  
  def testGetAllPermissions(self):
    # get_all_permissions should return all permissions as bound to the group
    permissions = [permission.get_permission(x) for x in ['Permission20','Permission21','Permission22','Permission23','Permission24']]
    identities = [i for i in identity.identity_query().order('email')]
    groups = [g for g in group.group_query().order('name')]
    self.assert_(len(groups[0].get_all_permissions()) == 5, 'Group must return the 5 bound permissions')
    self.assertEqual(frozenset(permissions), frozenset(groups[0].get_all_permissions()), 'Group must return the 5 bound permissions')
  
  def testHasPermission(self):
    # should return true for any permission bound to the group
    permissions = [permission.get_permission(x) for x in ['Permission20','Permission21','Permission22','Permission23','Permission24']]
    not_permissions = [permission.get_permission(n) for n in ['Permission0','Permission5','Permission8','Permission27','Permission35','Permission10','Permission13','Permission16']]
    identities = [i for i in identity.identity_query().order('email')]
    groups = [g for g in group.group_query().order('name')]
    for p in permissions:
      self.assert_(groups[0].has_permission(p), 'Group must return true for bound permissions')
    for p in not_permissions:
      self.assert_(not groups[0].has_permission(p), 'Group must return false for unbound permissions')
      
  def testGetAllMembers(self):
    # should return all group members
    identities = [identity.get_identity(x) for x in ['User0@example.org','User1@example.org','User2@example.org','User3@example.org','User4@example.org']]
    g = group.get_group('Group0')
    self.assert_(frozenset(identities) == frozenset(g.get_all_members()), 'Group must return all bound members')
    self.assert_(len(g.get_all_members()) == 5, 'Group must return all bound members')
    
  def testHasMember(self):
    # return true when passed an identity that belongs to this group
    identities = [identity.get_identity(x) for x in ['User0@example.org','User1@example.org','User2@example.org','User3@example.org','User4@example.org']]
    g = group.get_group('Group0')
    for i in identities:
      self.assert_(g.has_member(i), 'Group must return true for all identities that belong to group')
      
class GroupHasMembers(unittest.TestCase):
  def setUp(self):
    identities = []
    for i in range(20):
      identities.append(identity.create_identity('User'+str(i)+'@example.org'))
    groups = []
    for g in range(4):
      groups.append(group.create_group('Group'+str(g)))
    permissions = []
    for p in range(40):
      permissions.append(permission.create_permission('Permission'+str(p)))
    for r in [(0,5,0),(5,10,1),(10,15,2),(15,20,3)]:
      for i in identities[r[0]:r[1]]:
        group.add_member(groups[r[2]],i)
    for r in range(20):
      permission.bind_permission(permissions[r],identities[r])
    for r in [(20,25,0),(25,30,1),(30,35,2),(35,40,3)]:
      for p in permissions[r[0]:r[1]]:
        permission.bind_permission(p,groups[r[2]])
  
  def testValidIdentities(self):
    # ensure that has_permissions return true given any combination of valid permissions
    identities = [identity.get_identity(x) for x in ['User0@example.org','User1@example.org','User2@example.org','User3@example.org','User4@example.org']]
    g = group.get_group('Group0')
    for i in range(1,5):
      self.assert_(g.has_members(identities[0:i]), 'Identity must return true to any combination of valid members')

  def testEmptyList(self):
    # ensure that has_permissions returns false for an empty list
    g = group.get_group('Group0')
    self.assert_(not g.has_members([]), 'Group must return false for an empty member list')

  def testInvalidIdentities(self):
    # ensure that has_permissions return false for any combination of invalid permissions
    g = group.get_group('Group0')
    identities = [identity.get_identity(n) for n in ['User11@example.org','User12@example.org','User18@example.org','User19@example.org','User15@example.org']]
    for i in range(len(identities)):
      self.assert_(not g.has_members(identities[0:i]), 'Identity must return false for any combination of non-members')
    
class GroupHasPermissions(unittest.TestCase):
  def setUp(self):
    identities = []
    for i in range(20):
      identities.append(identity.create_identity('User'+str(i)+'@example.org'))
    groups = []
    for g in range(4):
      groups.append(group.create_group('Group'+str(g)))
    permissions = []
    for p in range(40):
      permissions.append(permission.create_permission('Permission'+str(p)))
    for r in [(0,5,0),(5,10,1),(10,15,2),(15,20,3)]:
      for i in identities[r[0]:r[1]]:
        group.add_member(groups[r[2]],i)
    for r in range(20):
      permission.bind_permission(permissions[r],identities[r])
    for r in [(20,25,0),(25,30,1),(30,35,2),(35,40,3)]:
      for p in permissions[r[0]:r[1]]:
        permission.bind_permission(p,groups[r[2]])
  
  def testValidValues(self):
    # ensure that has_permissions return true given any combination of valid permissions
    permissions = [permission.get_permission(n) for n in ['Permission20','Permission21','Permission22','Permission23','Permission24']]
    identities = [i for i in identity.identity_query().order('email')]
    groups = [g for g in group.group_query().order('name')]
    for p in range(1,5):
      self.assert_(groups[0].has_permissions(permissions[0:p]), 'Group must return true to any combination of bound permissions')
    
  def testEmptyList(self):
    # ensure that has_permissions returns false for an empty list
    g = group.get_group('Group0')
    self.assert_(not g.has_permissions([]), 'Group must return false for an empty permission list')
    
  def testInvalidValues(self):
    # ensure that has_permissions return false for any combination of invalid permissions
    g = group.get_group('Group0')
    permissions = [permission.get_permission(n) for n in ['Permission0','Permission5','Permission8','Permission23','Permission35','Permission10','Permission13','Permission16']]
    for p in range(len(permissions)):
      self.assert_(not g.has_permissions(permissions[0:p]), 'Group must return false for any combination of unbound permissions')
      
    
      
    
    

