import unittest
from PGUserManager import identity
from PGUserManager import group
from PGUserManager import permission
from PGUserManager import exceptions
from PGUserManager import models
from google.appengine.ext import db
from google.appengine.api import memcache
import logging

class SubIdentity(models.Identity):
  """A subclass of models.Identity"""
  pass

class SubClassTesting(unittest.TestCase):
  """Test subclassing the identity models"""
  def setUp(self):
    [identity.create_identity(email_address,klass=SubIdentity) for email_address in ['sub1@example.org','sub2@example.org','sub3@example.org']]
    
  def test_RetrieveSubIdentity(self):
    """use the get_identity function to retrieve a subclassed identity object"""
    i = identity.get_identity('sub1@example.org',klass=)
    self.assert_(isinstance(i,SubIdentity), 'Retrieved identity must be an instance of the identity subclass')
    self.assert_(i.email == 'sub1@example.org', 'Retrieved identity must have the email that was queried for')
    
    
        