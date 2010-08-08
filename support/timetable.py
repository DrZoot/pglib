"""
timetable.py

Created by Paul Gower on 08/08/10.
Copyright (c) 2010 Monotone Software. All rights reserved.

Timetable support functions (Days / Periods)
"""
from model.day import Day
from model.period import Period
from support.identity import user_domain

def get_days():
  """return an ordered list of days for this domain"""
  domain = user_domain()
  days_query = Day.all().filter('domain',domain)
  if days_query.count() == 0:
    days_query = Day.all().filter('domain','*')
  days_query.order('number')
  results = []
  for day in days_query:
    results.append(day)
  return results
  