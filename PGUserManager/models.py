"""
models.py
PGUserManager

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

Models for PGUserManager
"""
from google.appengine.ext import db

# Group Model
"""
Name: Group
Properties:
Name : String : The name of the group. Must be unique.
Description: String: A description for this group, optional.
"""

# Permission Model
"""
Name: Permission
Properties:
Name : String : The name of the Permission. Must be unique.
Description : String : A description for the permission, optional.
"""

# Permission Binding Model (Polymorphic)
"""
Name: PermissionBinding
Properties:
Permission : Key : The key for the permission that this binding applies to.
"""
# Group Permission Binding Model
"""
Name: GroupPermissionBinding
Inherits from Permission Binding
Properties:
Group : Key : The key for the group that this permission binds to.
(Inherited) Permission : Key : See parent.
"""
# User Permission Binding Model
"""
Name: UserPermissionBinding
Inherits from Permission Binding
Properties:
User : User : The user that this permission binds to.
(Inherited) Permission : Key : See parent.
"""

# Membership Binding Model
"""
Name: GroupMembershipBinding
Properties:
User : User : The user that is bound.
Group : Key : The group they are bound to.
"""
