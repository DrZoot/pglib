import models
import logging
import types
from google.appengine.api import users
from google.appengine.api import memcache

logging.info(str(type(models)))
# IMPORTANT: this module ignores the USE_MEMCACHE constant and always caches
  
# memcache index generators
U_INDEX=lambda c,k: "user_"+c.nickname()+"_"+k
G_INDEX=lambda k: "global_"+k

def get(index, user_first=False, default=None):
  """
  Get and return a settings value for the specified index. If user_first then search for a user value to override the global value first.
  Use memcache to store query results for speedups in future.
  """
  index = str(index)
  current_user = users.get_current_user()
  m_client = memcache.Client()
  u_value = m_client.get(U_INDEX(current_user,index))
  if user_first and not u_value:
    u_setting = models.Setting.get_by_key_name(U_INDEX(current_user,index))
    if u_setting:
      u_value = u_setting.value
  if user_first and u_value:
    m_client.set(U_INDEX(current_user,index),u_value)
    return u_value
  g_value = m_client.get(G_INDEX(index))
  if not g_value:
    g_setting = models.Setting.get_by_key_name(G_INDEX(index))
    if g_setting:
      g_value = g_setting.value
  if g_value:
    m_client.set(G_INDEX(index),g_value)
    return g_value
  logging.warning("pglib.settings: could not find setting with index: "+G_INDEX(index)+" or "+U_INDEX(current_user,index))
  return default
      
def set(index, value, is_global=False):
  """
  Set both the value of the datastore settings object and also the memcache record
  """
  index = str(index)
  logging.info(str(type(models.Setting)))
  current_user = users.get_current_user()
  m_index = G_INDEX(index) if is_global else U_INDEX(current_user,index)
  m_client = memcache.Client()
  s = models.Setting.get_by_key_name(m_index)
  if s:
    s.value = value
  else:
    s = models.Setting(key_name=m_index,index=index,value=value,is_global=is_global)
  s.put()
  m_client.set(m_index,value)
  return s
  
def load(yaml_file):
  """
  load a sreies of settings from a yaml file
  """
  #TODO: this function...
  return None