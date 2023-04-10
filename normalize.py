# normalize.py for normalize-stripe-emails by maxtheaxe

import argparse
import csv
from datetime import datetime
import os
from dotenv import load_dotenv
import stripe


def get_config():
	load_dotenv()  # import env vars from .env file
	stripe.api_key = os.environ['STRIPE_API_KEY']


def save_mapping(email_mapping):
	# unique filename for current time
	now = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
	# save mapping for all customers (with emails), changed or not
	with open(f"email_mapping_{now}.csv", "w", encoding="UTF8", newline="") as f:
		writer = csv.writer(f)
		writer.writerow(("customer id", "old email", "new email"))
		writer.writerows(email_mapping)
	print(f"record saved to email_mapping_{now}.csv")
	return


def normalize_emails(oversight, verbose):
	print("checking customer list for uppercase emails...")
	customers = stripe.Customer.list()
	email_mapping = [] # collect mapping for logging purposes
	for customer in customers:
		# verify that an email is actually listed
		if customer["email"] is None:
			if verbose:
				print(f'no email listed for customer {customer["id"]}, skipping')
		else: # skip if no email listed
			lower_email = customer["email"].lower()
			# for the sake of records, will be changed to reflect result
			new_email = customer["email"]
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
					# record that email was updated for given customer
					new_email = lower_email
			elif verbose:
				print(f'{customer["email"]} ->')
			# save record of original email and "new" (possibly unchanged) email
			email_mapping.append(
				(customer["id"], customer["email"], new_email))
	return email_mapping


def main(args):
	get_config()
	email_mapping = normalize_emails(args.oversight, args.verbose)
	save_mapping(email_mapping)


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