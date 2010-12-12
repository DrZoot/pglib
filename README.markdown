# PGUserManager
## Description
PGUserManager is a library for Google App Engine that provides management for Users,Groups and Permissions. It is loosely based on the django.contrib.auth module. 
PGUserManager does not involve itself with the actual authentication process of App Engine, it merely allows you to create groups and permissions and bind users to them.
Please send any feedback to p 'dot' gower 'at' gmail 'dot' com.

## TODO
* General
  * Figure out how to do read only properties, there are whole bunches of stuff that i dont want people to be able to change ever
  * use the results of the below tests to optimize all read operations
  * make sure all models have methods to retrieve all of their dependants
  * memcache stuff
  * setup some sort of profiling
  * add logging to everything
  * implement some way to hook into the existing authentication mechanism and create new identities for new users
  * do we play nice with openid?
  * check to make sure the email attribute passed to identity actually looks like an email address
  * when changing attributes on an identity get setattr to invalidate all dependent cache data
  * re-evaluate `add_dependent` and `remove_dependent`
  * would hashing all of the input args give better keys?
  * what happens when someone makes changes to the user data via the admin console (googles not mine)?
  * revist the membership_binding pre call hooks, theyre not efficient
  * rewrite identity `__repr__` to deal with dynamic properties
  * hook into delete calls and make sure remove_dependants is called in that circumstance too
  
* Completed
  * DONE - add tests to make sure inactive identities are not returned in group operations
  * DONE - make all methods obey active status, except xx_query
  * DONE - Modify tests to be a bit more efficient
  * DONE - Integrate Identity active checking in all queries
    * Identities must be considered hidden when active is false
    * If groups dont return inactive members then there will be no way to get inactive group members, add a switch to get_identity to return inactive members, add a switch to get_members to return inactive members
  * DONE - make create_identity accept an unlimited number of kwarg arguments and then turn them into dynamic params on the identity