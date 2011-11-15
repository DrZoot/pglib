import models
import logging

def get (key)
  i = models.Setting.all().filter('key =',key).get()
  if i:
    return i
  else:
    logging.error("Could not find settings key: " + key)
    
def set (key, value)
  t = type(value)
  if t == str:
    return models.StringSetting(key=key,value=value).put()
  elif t == int:
    return models.IntSetting(key=key,value=value).put()
  elif t == bool:
    return models.BoolSetting(key=key,value=value).put()
  else:
    logging.error("Unsupported setting type: " + str(type(value)))
    return False