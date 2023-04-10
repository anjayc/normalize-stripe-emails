# normalize-stripe-emails
force all stripe customer emails to lowercase via API

## why?
* emails in the old portal were not sanitized to remove uppercase characters
* the new portal, for which users were forced to create new accounts, did force lowercase
* this is an alternative to adding an extra step in which all components refer to a record of lowercase emails, along with their capitalized counterparts
