import models
import logging
import types
import utils
from google.appengine.api import users
from google.appengine.api import memcache

logging.info(str(type(models)))
# IMPORTANT: this module ignores the USE_MEMCACHE constant and always caches
  
# memcache key and db key_name generators
USER_KEY=lambda c,k: "user_"+c.nickname()+"_"+k
GLOBAL_KEY=lambda k: "global_"+k

def get(index, user_first=False, default={}):
  """
  Get and return a settings value for the specified index. If user_first then search for a user value to override the global value first.
  Use memcache to store query results for speedups in future.
  """
  index = str(index)
  current_user = users.get_current_user()
  m_client = memcache.Client()
  # find the user setting first (if user_first)
  if user_first:
    key = USER_KEY(current_user,index)
    u_value = m_client.get(key)
    if u_value:
      return u_value
    u_setting = models.Setting.get_by_key_name(key)
    if u_setting:
      u_value = utils.expando_prop_dict(u_setting)
      m_client.set(key,u_value)
      return u_value
  # try to retrieve the global setting using a calculated key_name
  key = GLOBAL_KEY(index)
  g_value = m_client.get(key)
  if g_value:
    return g_value
  else:
    g_setting = models.Setting.get_by_key_name(key)
    if g_setting:
      g_value = utils.expando_prop_dict(g_setting)
      m_client.set(key,g_value)
      return g_value
  logging.warning("pglib.settings: could not find setting with index: "+GLOBAL_KEY(index)+" or "+USER_KEY(current_user,index))
  return default
   
def set(index, is_global=False, **kwargs):
  """
  Set both the value of the datastore settings object and also the memcache record
  """
  index = str(index)
  current_user = users.get_current_user()
  key = GLOBAL_KEY(index) if is_global else USER_KEY(current_user,index)
  m_client = memcache.Client()
  #m_client.delete(m_index)
  s = models.Setting.get_by_key_name(key)
  if s:
    s = utils.update_expando(s,kwargs)
  else:
    s = models.Setting(key_name=key,index=index,is_global=is_global,**kwargs)
  s.put()
  m_client.set(key,utils.expando_prop_dict(s))
  return s
  
def load(yaml_file):
  """
  load a sreies of settings from a yaml file
  """
  #TODO: this function...
  return None