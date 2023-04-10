# normalize.py for normalize-stripe-emails by maxtheaxe

import argparse
import os
from dotenv import load_dotenv
import stripe


def get_config():
	load_dotenv()  # import env vars from .env file
	stripe.api_key = os.environ['STRIPE_API_KEY']


def normalize_emails(oversight, verbose):
	print("checking customer list for uppercase emails...")
	customers = stripe.Customer.list()
	for customer in customers:
		# verify that an email is actually listed
		if customer["email"] is None:
			if verbose:
				print(f'no email listed for customer {customer["id"]}, skipping')
		else: # skip if no email listed
			lower_email = customer["email"].lower()
			# if the current customer's email has any uppercase characters
			if not (customer["email"] == lower_email):
				approval = True
				# show preview of email change
				print(f'{customer["email"]} -> {lower_email}')
				if oversight: # if we're running interactively with manual input
					# any response aside from "true", "yes", or "y" is a refusal
					approval_request = input("\tapproved? ")
					if all(approval_request.lower() != answer for answer in ["true", "yes", "y"]):
						print("\tno change")
						approval = False
					else:
						print("\temail updated")
				if approval:
					stripe.Customer.modify(
						customer["id"],
						email=lower_email,
					)
			elif verbose:
				print(f'{customer["email"]} ->')


def main(args):
	get_config()
	normalize_emails(args.oversight, args.verbose)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog='Stripe Customer Email Normalizer',
		description='Converts existing customer emails to lowercase.'
	)
	# by default, operate fully automatically, and don't print messages
	# regarding customers with no change
	parser.add_argument("-o", "--oversight", default=False, action="store_true")
	parser.add_argument("-v", "--verbose", default=False, action="store_true")
	main(parser.parse_args())