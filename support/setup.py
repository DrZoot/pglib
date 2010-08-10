"""
setup.py

Created by Paul Gower on 08/08/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Setup functions run when a new domain admin logs in
"""
from model.group import Group
from model.right import Right
from model.day import Day
from model.period import Period
from model.domain import Domain
from datetime import time
from support.identity import user_domain_name
from google.appengine.api import users

def application_setup():
  """
  setup the application wide groups and rights
  this should only be once _ever_. if for some reason the db gets
  deleted then this should be rerun
  """
  # Shared Application Rights
  managers_rights = Right(name="RESOURCE_MANAGER")
  managers_rights.put()
  editors_rights = Right(name="RESOURCE_EDITOR")
  editors_rights.put()

def domain_setup(name):
  """setup for each domain"""
  domain = Domain(name=name,contact=users.get_current_user())
  domain.put()
  # Default Groups
  viewers = Group(name='Viewers',domain=domain)
  viewers.put()
  editors = Group(name='Editors',domain=domain)
  editors.put()
  managers = Group(name='Managers',domain=domain)
  managers.put()  
  # Days + Periods
  day_numbers = [1,2,3,4,5]
  periods = [('Before School',time(7,30),time(8,30)),('Period 1',time(8,30),time(10,30)),('Period 2',time(10,30),time(11,10)),('Morning Tea',time(11,10),time(11,30)),('Period 3',time(11,30),time(12,20)),('Period 4',time(12,20),time(13,10)),('Lunch',time(13,10),time(13,50)),('Period 5',time(13,50),time(14,30)),('Period 6',time(14,30),time(15,15)),('After School',time(15,15),time(17,00))]
  for i in day_numbers:
    current_day = Day(number=i,domain=domain)
    current_day.put()
    for period in periods:
      p = Period(day=current_day,name=period[0],start=period[1],end=period[2])
      p.put()
  
# def is_domain_setup():
#   """returns true if this domain is setup"""
#   domain = user_domain()
#   days_count = Day.all().filter('domain',domain).count()
#   if days_count == 0:
#     return False
#   else:
#     return True
  
  
  
  
  
  