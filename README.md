# normalize stripe emails
force all stripe customer emails to lowercase via API

## why?
* your current customer emails were not case-sanitized on collection
* stripe customer email search is case-sensitive [(reference)](https://stackoverflow.com/q/73309133/4513452)
* this is an alternative to adding an extra step in which all components refer to a record of lowercase emails, along with their capitalized counterparts

## how?
**clone the repo**

`git clone https://github.com/maxtheaxe/normalize-stripe-emails.git`

**install dependencies**

`pip3 install -r requirements.txt`

**run the script** *(bracketed optional arguments)*

`python3 normalize.py [--oversight] [--verbose]`

## notes
* use at your own risk
* supports manual approval of changes (with `--oversight` flag)
* creates mapping of original emails to new ones, exported to a csv
* if your customer uses different account and billing emails, this will only change their account email