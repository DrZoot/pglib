import models
import logging
from google.appengine.api import users
from google.appengine.api import memcache

# IMPORTANT: this module ignores the USE_MEMCACHE constant and always caches
  
# memcache key generators
U_KEY=lambda: "user_"+current_user.nickname()+"_"+key
G_KEY=lambda: "global_"+key

def get(key, user_first=False, default=None)
  """
  Get and return a settings value for the specified key. If user_first then search for a user value to override the global value first.
  Use memcache to store query results for speedups in future.
  """
  current_user = users.get_current_user()
  m_client = memcache.Client()
  u_value = m_client.get(U_KEY)
  if not u_value:
    u_setting = models.Setting.get_by_key_name(U_KEY)
    if u_setting:
      u_value = u_setting.value
  if user_first and u_value:
    m_client.set(U_KEY,u_value)
    return u_value
  g_value = m_client.get(G_KEY)
  if not g_value:
    g_setting = models.Setting.get_by_key_name(G_KEY)
    if g_setting:
      g_value = g_setting.value
  if g_value:
    m_client.set(G_KEY,g_value)
    return g_value
  logging.warning("pglib.settings: could not find setting with key: "+G_KEY+" or "+U_KEY)
  return default
      
def set(key, value, is_global=False)
  """
  Set both the value of the datastore settings object and also the memcache record
  """
  current_user = users.get_current_user()
  m_key = G_KEY if is_global else U_KEY
  m_client = memcache.Client()
  s = models.Setting.get_by_key_name(m_key)
  if s:
    s.value = value
  else:
    t = type(value)
    if t == str:
      s = models.StringSetting(key_name=m_key,key=key,value=value,is_global=is_global)
    elif t == int:
      s = models.IntSetting(key_name=m_key,key=key,value=value,is_global=is_global)
    elif t == bool:
      s = models.BoolSetting(key_name=m_key,key=key,value=value,is_global=is_global)
    elif t == float:
      s = models.FloatSetting(key_name=m_key,key=key,value=value,is_global=is_global)
    else:
      logging.error("Unsupported setting type: " + str(type(value)))
      return None
  s.put()
  m_client.set(m_key,value)
  return s
  
def load(yaml_file)
  """
  load a sreies of settings from a yaml file
  """
  #TODO: this function...
  return None