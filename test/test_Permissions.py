import unittest
import permissions
from google.appengine.api import memcache
from google.appengine.ext import db
import logging

class PermissionTests(unittest.TestCase):
  def setUp(self):
    memcache.flush_all()
    
  def test_CreatePermission(self):
    # test creating permission, both object based and action based
    p1 = permissions.create("read",desc="User can read something")
    self.assert_(isinstance(p1,permissions.models.Permission),"Must return a valid permission instance")
    p2 = permissions.create("write")
    self.assert_(isinstance(p2,permissions.models.Permission),"Must return a valid permission instance")
    p3 = permissions.create("hit",obj=p1,desc="Users can hit the read permission")
    self.assert_(isinstance(p3,permissions.models.Permission),"Must return a valid permission instance")
    p4 = permissions.create("hit",obj=p2)
    self.assert_(isinstance(p4,permissions.models.Permission),"Must return a valid permission instance")
  
  def test_DuplicatePermission(self):
    # test creating a permission that is the same as an existing one
    p1 = permissions.create('read')
    p2 = permissions.create('read')
    self.assert_(p1.key() == p2.key(),"Attempts to create permissions with the exact same details should return the exiting permission instance")
    
  def test_GetPermission(self):
    # test that search for a permission results in the permission being returned
    p1 = permissions.create("read")
    logging.info(p1)
    p5 = permissions.get("read")
    logging.info(p5)
    p2 = permissions.create('write',desc="a writing permission")
    p3 = permissions.create('furgle',p1)
    p4 = permissions.create('nurgle',p2,desc="permission to nurgle p2")
    self.assert_(p1 == permissions.get("read"),"should return the generic read permission")
    self.assert_(p2 == permissions.get('write'),"should return the generic write permission")
    self.assert_(p3 == permissions.get('furgle',obj=p1),"should return the permission to furgle p1")
    self.assert_(p4 == permissions.get('nurgle',obj=p2),"should return the permissions to nurgle p2")
    self.assert_(permissions.get('bingle') == None,"trying to get permissions that dont exist should return None")
    self.assert_(permissions.get('bingle',obj=p1) == None,"trying to get permissions that dont exist should return None")
    
  def test_DeletePermission(self):
    # test that a deleted permission is actually gone
    p1 = permissions.create('read')
    p2 = permissions.get('read')
    self.assert_(p1 == p2,"stored permission must be returned")
    permissions.delete(p1)
    p3 = permissions.get('read')
    self.assert_(p3 == None,"deleted permissions should not be returned")
    
  def test_ObjectBinding(self):
    # test that permissions can be bound to objects
    class TestObject(db.Model):
      name = db.StringProperty(required=True)
      def __str__(self):
        return "TestObject:"+self.name
    o1 = TestObject(name="John").put()
    o2 = TestObject(name="Paul").put()
    o3 = TestObject(name="George").put()
    o4 = TestObject(name="Ringo").put()
    p1 = permissions.create('read')
    p2 = permissions.create('write')
    permissions.bind(p1,o1,o2,o3,o4)
    permissions.bind(p2,o3,o4)
    self.assert_(permissions.has_permission(o1,p1),"should return true for permission")
    self.assert_(permissions.has_permission(o2,p1),"should return true for permission")
    self.assert_(permissions.has_permission(o3,p1),"should return true for permission")
    self.assert_(permissions.has_permission(o4,p1),"should return true for permission")
    self.assert_(permissions.has_permission(o1,p2) == False,"object 1 should not have this permission")
    self.assert_(permissions.has_permission(o2,p2) == False,"object 2 should not have this permission")
    self.assert_(permissions.has_permission(o3,p2),"should return true for permission")
    self.assert_(permissions.has_permission(o4,p2),"should return true for permission")
    
  def test_GroupBinding(self):
    # test that when groups are bound they bind all their members
    pass
    