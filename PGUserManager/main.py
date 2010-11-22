"""
main.py

Created by Paul Gower on 2010-11-10.
Copyright 2010 Monotone Software. All rights reserved.

PGUserManager - User management API that uses BigTable for storage.
"""
import models
from google.appengine.api import users

# ============
# = Identity =
# ============
"""
Things this needs to do:
Create new identity:
The user email address will be provided for this.
If the email address provided already exists this raises an error

Modify identity user email:
This only covers changing the email address, this ensures that no two users have the same email address.
If an attempt is made to change the email address to one that already exists this raises the EmailAddress

Delete identity:
Needs to delete the identity and then delete any permission bindings or membership bindings that have the user as a subject.

exists?:
given an email address returns true if an identity exists for the email address or false if not

EmailAlreadyAssigned (Error):
Raised if an attempt is made to create an identity with an email address thats already been used.
Error contains the identity which already uses the email address.
"""

# =========
# = Group =
# =========
"""
Stuff this needs to do:
Create a new group:
A name 
"""

# ==============
# = Permission =
# ==============

