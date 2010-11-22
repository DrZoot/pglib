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
  name = db.StringProperty(required=True)
  description = db.TextProperty()
  
class Permission (db.Model):
  """
  --Description--
  Stores a permission. (A permission is just a text key, your either associated or your not).
  --Properties--
  Name : StringProperty : The name of the property, must be unique.
  Description : TextProperty : Optional property description.
  """
  name = StringProperty(required=True)
  description = TextProperty()
  
class Identity (db.Expando):
  """
  --Description--
  Stores a users information and mapping to a user object. Also used to represent users as datastore objects.
  Also stores arbitrary user information.
  --Properties--
  User : UserProperty : A user object.
  """
  user = UserProperty(required=True)

class PermissionBinding (db.Model):
  """
  --Description--
  Represents relationships between permissions and groups / users.
  --Properties--
  Permission : ReferenceProperty(Permission) : A reference to the permission being bound.
  Subject : ReferenceProperty : A reference to the item being bound to the permission. Must be either a group or an identity.
  """
  permission = ReferenceProperty(reference_class=Permission,required=True)
  subject = ReferenceProperty(required=True)

class MembershipBinding (db.Model):
  """
  --Description--
  Object for storing user group membership.
  --Properties--
  Identity : ReferenceProperty : The user identity to be bound.
  Group : ReferenceProperty : The group to be bound.
  """
  identity = ReferenceProperty(required=True,reference_class=Identity)
  group = ReferenceProperty(required=True,reference_class=Group)
