"""
models.py
PGUserManager

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

Models for PGUserManager
"""
from google.appengine.ext import db

class Group (db.Model):
  """
  --Description--
  Stores a group.
  --Properties--
  Name : StringProperty : The name of the group, must be unique, cannot be administrators, users.
  Description : TextProperty : Optional group description.
  """
  
class Permission (db.Model):
  """
  --Description--
  Stores a permission. (A permission is just a text key, your either associated or your not).
  --Properties--
  Name : StringProperty : The name of the property, must be unique.
  Description : TextProperty : Optional property description.
  """

class PermissionBinding (db.PolyModel):
  """
  --Description--
  Parent class for permission binding objects. Represents relationships between permissions and groups / users.
  --Properties--
  Permission : ReferenceProperty(Permission) : A reference to the permission being bound.
  """
  
class GroupPermissionBinding (PermissionBinding):
  """
  --Description--
  Child of PermissionBinding that represents the binding between a permission and a group.
  --Properties--
  Permission (INHERITED)
  Group : ReferenceProperty(Group) : The group the permission is being bound to.
  """
  
class UserPermissionBinding (PermissionBinding):
  """
  --Description--
  Child of permission binding that represents the binding between a permission and a user.
  --Properties--
  Permission (INHERITED)
  User : UserProperty : The ser the permission is being bound to.
  """

class MembershipBinding (db.Model):
  """
  --Description--
  Object for storing user group membership.
  --Properties--
  User : UserProperty : The user to be bound.
  Group : ReferenceProperty : The group to be bound.
  """
