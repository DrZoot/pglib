import unittest
import settings
import random
import types
from google.appengine.api import memcache


# supported types
supported_types = {
'a_bool' : (True,bool),
'a_int' : (56, (int,long)),
'a_float' : (134.52, float),
'a_string' : ("FooBAR",(str,unicode)),
'a_list' : ([1,2,3,4,'five','six'],list),
'a_none' : (None,types.NoneType),
}

# unsupported types
unsupported_types = {
'a_function' : (lambda: "hello world",types.FunctionType),
}

IS_GLOBAL = True if random.randint(0,1) == 1 else False

class GlobalSettingTests (unittest.TestCase):

  def setUp(self):
    memcache.flush_all()

  def test_createBasicSetting(self):
    # test the creation of a basic settings object
    a_string = "BARfoo"
    an_index = "BARfoo_global_setting"
    s = settings.set(an_index,a_string,is_global=IS_GLOBAL)
    self.assert_(s.value == a_string, "Stored value: "+a_string+" retrieved: "+str(s.value))
    self.assert_(s.index == an_index, "Provided key: "+an_index+" retrieved: "+str(s.index))

  def test_settingTypes(self):
    # test the creation of settings with different types
    for k,v in supported_types.iteritems():
      s = settings.set(k,v[0],is_global=IS_GLOBAL)
      self.assert_(s,k+" should create a valid settings object")
    for k,v in unsupported_types.iteritems():
      s = settings.set(k,v[0],is_global=IS_GLOBAL)
      self.assert_(s == None, "Unsupported types should return None")

  def test_settingRetrievalTypes(self):
    # test that the type of value returned matches the type of the value passed in
    for k,v in supported_types.iteritems():
      s = settings.set(k,v[0],is_global=IS_GLOBAL)
      t = settings.models.Setting.get(s.key())
      self.assert_(isinstance(t.value,v[1]), k+" Passed value type: "+str(type(s.value))+" Retrieved value type: "+str(type(t.value)))
      
  def test_settingRetrievalValue(self):
    # test that the value returned matches the value passed in
    for k,v in supported_types.iteritems():
      s = settings.set(k,v[0],is_global=IS_GLOBAL)
      t = settings.models.Setting.get(s.key())
      self.assert_(v[0] == t.value, "Retireved value:"+str(t.value)+" does not match stored value: "+str(v[0]))
   
  def test_NonStringIndex(self):
    # test what happens when a non string index is used
    a_value = "BARfoo"
    an_index = 432521
    s = settings.set(an_index,a_value,is_global=IS_GLOBAL)
    self.assert_(s != None, "Non-string keys should be converted")
    
  def test_SettingOverwriting(self):
    # test that values are updated when settings are overwritten
    s = settings.set('an_index',12345,is_global=IS_GLOBAL)
    t = settings.set('an_index',67890,is_global=IS_GLOBAL)
    self.assert_(s.key() == t.key(), "Set function should not create new objects when existig objects with the same index exist")
    self.assert_(s.value == 12345, "Initial value should remain in initial object")
    self.assert_(t.value == 67890, "Updated value should overwrite old value")
    
  def test_SettingHierarchy(self):
    # test that user settings overwrite global settings where they are present
    g = settings.set('an_index','global value',is_global=True)
    u = settings.set('an_index','user value')
    self.assert_(g.key() != u.key(),"User settings should not overwrite global settings")
    s_one = settings.get('an_index') #should be global
    self.assert_(s_one == 'global value',"settings.get should return the global value unless user_first is set")
    s_two = settings.get('an_index',user_first=True)
    self.assert_(s_two == 'user value',"User setting should be returned in favour of the global setting when user_first is True")
    
  def test_GetDefaultValue(self):
    # test that the settings.get function returns the default value when it cant find an index
    pass