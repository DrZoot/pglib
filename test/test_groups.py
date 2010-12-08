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

  def test_CreateGroup(self):
    # creating a group should return the created group object
    g = group.create_group('Group1')
    self.assert_(isinstance(g,models.Group), 'Create group must return an object of type Group')
    self.assert_(g.name == 'Group1', 'Returned group must be the one created')
    
  def test_CreateDuplicateGroup(self):
    # creating a group with a use group name should raise a duplicatevalue error
    group.create_group('Group1')
    def create_dupe_group():
      return group.create_group('Group1')
    self.assertRaises(exceptions.DuplicateValue, create_dupe_group)
    
  def test_RetrieveGroupByName(self):
    # retrieve a group from the datstore by name
    group.create_group('Group1')
    g = group.get_group('Group1')
    self.assert_(isinstance(g,models.Group), 'Must return an object of type Group')
    self.assert_(g.name == 'Group1', 'Returned group must be the one created')
    
  def test_CreateGroupQuery(self):
    # create a custom query for groups
    self.assert_(isinstance(group.group_query(),db.Query), 'group.group_query must return db.Query type')
    
  def test_DeleteGroup(self):
    # delete a group
    g = group.create_group('Group1')
    g.delete()
    self.assert_(group.get_group('Group1') == None, 'Deleted group should not exist on the datastore')
    
  def test_AddIdentitiesToGroup(self):
    # add identities to a group
    g = group.create_group('Group1')
    identities = [ident for ident in identity.identity_query()]
    for ident in identities:
      g.add_member(ident)
    self.assertEqual(10, g.identity_bindings.count(), 'Number of membership bindings must equal the number of identities bound (10)')
    
  def test_AddIdentitiesToMultipleGroups(self):
    # add identities to a group
    g = group.create_group('Group1')
    g2 = group.create_group('Group2')
    identities = [ident for ident in identity.identity_query()]
    for ident in identities:
      g.add_member(ident)
      g2.add_member(ident)
    self.assertEqual(10, g.identity_bindings.count(), 'Number of membership bindings must equal the number of identities bound (10)')
    self.assertEqual(10, g2.identity_bindings.count(), 'Number of membership bindings must equal the number of identities bound (10)')
    
  def test_AddIdentitiesToGroupKeysOnly(self):
    # add identities to a group, use keys for the identities
    g = group.create_group('Group1')
    i_keys = [ik for ik in identity.identity_query(keys_only=True)]
    for ik in i_keys:
      g.add_member(ik)
    self.assertEqual(10, group.get_group('Group1').identity_bindings.count(), 'Number of membership bindings must equal the number of identities bound (10)')
    
class InstanceMethodTesting(unittest.TestCase):
  def setUp(self):
    identities = [identity.create_identity(i) for i in ['user1@example.org','user2@example.org']]
    groups = [group.create_group(g) for g in ['Group1','Group2']]
    group_permissions = [permission.create_permission(p) for p in ['GroupPermission1','GroupPermission2']]
    identity_permissions = [permission.create_permission(p) for p in ['IdentityPermission1','IdentityPermission2']]
    for p in group_permissions:
      p.bind_to(groups[0])
    for p in identity_permissions:
      p.bind_to(identities[0])
  
  def test_GetAllPermissions(self):
    # get_all_permissions should return all permissions as bound to the group
    permissions = [permission.get_permission(x) for x in ['GroupPermission1','GroupPermission2']]
    g = group.get_group('Group1')
    self.assert_(len(g.get_all_permissions()) == 2, 'Group must return the 2 bound permissions')
    self.assertEqual(frozenset(permissions), frozenset(g.get_all_permissions()), 'Group must return the 2 bound permissions')
  
  def test_HasPermission(self):
    # should return true for any permission bound to the group
    g = group.get_group('Group1')
    permissions = [permission.get_permission(x) for x in ['GroupPermission1','GroupPermission2']]
    for p in permissions:
      self.assert_(g.has_permission(p), 'Group must return true for bound permissions')
      
  def test_GetAllMembers(self):
    # should return all group members
    i = identity.get_identity('user1@example.org')
    g = group.get_group('Group1')
    g.add_member(i)
    self.assert_(frozenset([i]) == frozenset(g.get_all_members()), 'Group must return all bound members')
    
  def test_HasMember(self):
    # return true when passed an identity that belongs to this group
    i = identity.get_identity('user1@example.org')
    g = group.get_group('Group1')
    g.add_member(i)
    self.assert_(g.has_member(i), 'Group must return true for members')
      
class GroupHasMembers(unittest.TestCase):
  def setUp(self):
    identities = [identity.create_identity(i) for i in ['user1@example.org','user2@example.org']]
    groups = [group.create_group(g) for g in ['Group1','Group2']]
    groups[0].add_member(identities[0])
    groups[1].add_member(identities[1])
  
  def test_ValidIdentities(self):
    # ensure that has_permissions return true given any combination of valid permissions
    i = identity.get_identity('user1@example.org')
    g = group.get_group('Group1')
    self.assert_(g.has_member(i), 'Group must return true for valid members')

  def test_EmptyList(self):
    # ensure that has_permissions returns false for an empty list
    g = group.get_group('Group1')
    self.assert_(not g.has_members([]), 'Group must return false for an empty member list')

  def test_InvalidIdentities(self):
    # ensure that has_permissions return false for any combination of invalid permissions
    g = group.get_group('Group1')
    i = identity.get_identity('user2@example.org')
    self.assert_(not g.has_member(i), 'Group must return false for invalid members')
    
class GroupHasPermissions(unittest.TestCase):
  def setUp(self):
    groups = [group.create_group(g) for g in ['Group1','Group2']]
    valid_permissions = [permission.create_permission(p) for p in ['ValidPermission1','ValidPermission2']]
    invalid_permissions = [permission.create_permission(p) for p in ['InvalidPermission1','InvalidPermission2']]
    for p in valid_permissions:
      p.bind_to(groups[0])
  
  def test_ValidValues(self):
    # ensure that has_permissions return true given any combination of valid permissions
    permissions = [permission.get_permission(p) for p in ['ValidPermission1','ValidPermission2']]
    g = group.get_group('Group1')
    self.assert_(g.has_permissions(permissions), 'Group must return true to any combination of bound permissions')
    
  def test_EmptyList(self):
    # ensure that has_permissions returns false for an empty list
    g = group.get_group('Group1')
    self.assert_(not g.has_permissions([]), 'Group must return false for an empty permission list')
    
  def test_InvalidValues(self):
    # ensure that has_permissions return false for any combination of invalid permissions
    g = group.get_group('Group1')
    permissions = [permission.get_permission(p) for p in ['InvalidPermission1','InvalidPermission2']]
    self.assert_(not g.has_permissions(permissions), 'Group must return false for any combination of unbound permissions')
    
class GroupWithInactiveMembers(unittest.TestCase):
  def setUp(self):
    g = group.create_group('Group1')
    identities = [identity.create_identity(i) for i in ['user1@example.org','user2@example.org','user3@example.org','user4@example.org']]
    for i in identities:
      g.add_member(i)
    
  def test_GetAllMembersWithInactives(self):
    # ensure that get all members does not return inactive group members (unless told to with include_inactive=True)
    g = group.get_group('Group1')
    identities = [identity.get_identity(i) for i in ['user1@example.org','user2@example.org','user3@example.org','user4@example.org']]
    self.assert_(frozenset(g.get_all_members()) == frozenset(identities), 'get_all_members should return all bound identities that are active')
    identities[0].active = False
    identities[0].put()
    self.assert_(frozenset(g.get_all_members()) == frozenset(identities[1:]), 'get_all_members should only return identities that are active')
    self.assert_(frozenset(g.get_all_members(include_inactive=True)) == frozenset(identities), 'get_all_members should return all identities regardless of active status when passed include_inactive')
    
  def test_HasMemberWithInactive(self):
    # ensure that has_member returns false when the given identity is inactive
    g = group.get_group('Group1')
    i = identity.get_identity('user1@example.org')
    self.assert_(g.has_member(i), 'has_member should return true for bound active identities')
    i.active = False
    i.put()
    self.assert_(not g.has_member(i), 'has_member should return false for inactive bound identities')
    self.assert_(g.has_member(i,include_inactive=True), 'has_member should return true for bound inactive identities when passed the include_inactive param')
    
  def test_HasMembersWithInactive(self):
    # ensure that has_members return false when bound but inactive identities are passed
    g = group.get_group('Group1')
    identities = [identity.get_identity(i) for i in ['user1@example.org','user2@example.org','user3@example.org','user4@example.org']]
    self.assert_(g.has_members(identities), 'has_members should return true if all identities passed are bound and active')
    identities[0].active = False
    identities[0].put()
    self.assert_(not g.has_members(identities), 'has_members should return false if not all identities passed are active and bound')
    self.assert_(g.has_members(identities[1:]))
    self.assert_(g.has_members(identities,include_inactive=True), 'has_members should return true if all passed identites are bound regardless of active status')
    
    
    
      
    
      
    
    

