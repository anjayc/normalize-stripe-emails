# normalize stripe emails
deal with unsanitized stripe emails easily: force them to lowercase, or save a mapping

## why?
* your current customer emails were not case-sanitized on collection
* stripe customer email search is case-sensitive [(reference)](https://stackoverflow.com/q/73309133/4513452)
* this is an alternative to adding an extra step in which all components refer to a record of lowercase emails, along with their capitalized counterparts

## how?
**clone the repo**

`git clone https://github.com/maxtheaxe/normalize-stripe-emails.git`

**install dependencies**

`pip3 install -r requirements.txt`

**set up stripe API key**

create a text file in the same directory named `.env`, type in `STRIPE_API_KEY=<your API key>`

**run the script** *(optional arguments are bracketed)*

`python3 normalize.py [--oversight] [--verbose] [--testmode] [--testdata]`

## notes
* use at your own risk
* supports manual approval of changes (with `--oversight` flag)
* supports test data generation (with `--testdata` flag)
* supports "test mode", in which changes are not pushed to stripe (with `--testmode` flag)
* test mode can also be used to create a mapping, if you'd rather not replace customer data, and would instead like to access it using an external record of lowercase emails
* creates mapping of original emails to new ones, exported to a csv
* if your customer uses different account and billing emails, this will only change their account email
* PRs are welcome