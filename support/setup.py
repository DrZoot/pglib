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
from support.identity import user_domain

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

def domain_setup():
  """setup for each domain"""
  domain = user_domain()
  # Days + Periods
  day_numbers = [1,2,3,4,5]
  periods = [('Before School',1),('Period 1',2),('Period 2',3),('Morning Tea',4),('Period 3',5),('Period 4',6),('Lunch',7),('Period 5',8),('Period 6',9),('After School',10)]
  for i in day_numbers:
    current_day = Day(number=i,domain=domain)
    current_day.put()
    for period in periods:
      p = Period(day=current_day,name=period[0],sequence=period[1])
      p.put()
  
def is_domain_setup():
  """returns true if this domain is setup"""
  domain = user_domain()
  days_count = Day.all().filter('domain',domain).count()
  if days_count == 0:
    return False
  else:
    return True
  
  
  
  
  
  