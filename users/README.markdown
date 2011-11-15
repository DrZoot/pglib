# pglib.users
## Description
users is a library for Google App Engine that provides management for Users,Groups and Permissions. It is loosely based on the django.contrib.auth module. 
users does not involve itself with the actual authentication process of App Engine, it merely allows you to create groups and permissions and bind users to them.
Please send any feedback to p 'dot' gower 'at' gmail 'dot' com.

## TODO
* General
  * make all of the memcache code optional
  * setup some sort of automated performance profiling similar to gaeunit
  * add logging to everything
  * implement some way to hook into the existing authentication mechanism and create new identities for new users
  * do we play nice with openid?
  * hook into db.delete calls and make sure remove_dependants is called in that circumstance too.
  * what happens when someone makes changes to the user data via the admin console (googles not mine)?
  * revisit the membership_binding pre call hooks, theyre not efficient
  * ensure that the hooks only get called when the objects in question are part of PGUserManager
  * update docs
  * write an admin interface to the user store
  * reorganise all of the tests, add more testing for subclassing
  * consider splitting BindingModel, and the contents of utils.py into a seperate module PGUtils
  
* Completed
  * DONE - add unit tests to test the email validator
  * DONE - re-evaluate `add_dependent` and `remove_dependent`, they seem to work well
  * DONE - check to make sure the email attribute passed to identity actually looks like an email address
  * DONE - finish adding memcache to functions
  * DONE - ensure that dependants are always added before values are put into memcache, better to have non-existant memcache keys than keys that never get removed because they have no dependents
  * DONE - would hashing all of the input args give better keys? No, hashing produces human unreadable keys and actually takes slightly longer than simply concatenating strings.
  * DONE - Work out which model properties should be read-only and enforce that by overriding the `__setattr__` method
  * DONE - when changing attributes on an identity get setattr to invalidate all dependent cache data (accomplished with the API hooks)
  * DONE - rewrite identity `__repr__` to deal with dynamic properties
  * DONE - make sure all models have methods to retrieve all of their dependants
  * DONE - add tests to make sure inactive identities are not returned in group operations
  * DONE - make all methods obey active status, except xx_query
  * DONE - Modify tests to be a bit more efficient
  * DONE - Integrate Identity active checking in all queries
    * Identities must be considered hidden when active is false
    * If groups dont return inactive members then there will be no way to get inactive group members, add a switch to get_identity to return inactive members, add a switch to get_members to return inactive members
  * DONE - make create_identity accept an unlimited number of kwarg arguments and then turn them into dynamic params on the identity
