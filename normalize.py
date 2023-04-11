# normalize.py for normalize-stripe-emails by maxtheaxe

import argparse
import csv
from datetime import datetime
import os
from dotenv import load_dotenv
from faker import Faker
import stripe


def get_config():
	"""retrieve stripe API key from .env file"""
	load_dotenv()  # import env vars from .env file
	stripe.api_key = os.environ['STRIPE_API_KEY']


def save_mapping(email_mapping):
	"""save mapping of customer ID, original email to newly-converted (or not) email"""
	# unique filename for current time
	now = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
	# save mapping for all customers (with emails), changed or not
	with open(f"email_mapping_{now}.csv", "w", encoding="UTF8", newline="") as f:
		writer = csv.writer(f)
		writer.writerow(("customer id", "old email", "new email"))
		writer.writerows(email_mapping)
	print(f"record saved to email_mapping_{now}.csv")
	return


def import_mapping(mapping_file):
	"""import mapping of customer IDs and emails from csv file"""
	mapping = []
	with open(mapping_file, newline='', encoding="UTF8") as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			if row[0] != "customer id":
				mapping.append(row)
	return mapping


def normalize_emails(oversight, verbose, test_mode):
	"""cast existing stripe customer emails to lowercase"""
	print("checking customer list for uppercase emails...")
	email_mapping = []  # collect mapping for logging purposes
	customers = stripe.Customer.list()
	last_customer = None  # track last returned customer for pagination
	page_counter = 0
	while len(customers) > 0:
		if verbose:
			print(f"current page: {page_counter}")
		for customer in customers:
			# verify that an email is actually listed
			if customer["email"] is None:
				if verbose:
					print(f'no email listed for customer {customer["id"]}, skipping')
			else:  # skip if no email listed
				lower_email = customer["email"].lower()
				# for the sake of records, will be changed to reflect result
				new_email = customer["email"]
				# if the current customer's email has any uppercase characters
				if not (customer["email"] == lower_email):
					approval = True
					# show preview of email change
					print(f'{customer["email"]} -> {lower_email}')
					if oversight:  # if we're running interactively with manual input
						# any response aside from "true", "yes", or "y" is a refusal
						approval_request = input("\tapproved? ")
						if all(approval_request.lower() != answer for answer in ["true", "yes", "y"]):
							print("\tno change")
							approval = False
						else:
							print("\temail updated")
					if approval:
						# only write results to stripe if not in test mode
						if not test_mode:
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
			last_customer = customer["id"]
		customers = stripe.Customer.list(starting_after=last_customer)
		page_counter += 1
	return email_mapping


def revert_emails(old_mapping):
	"""revert previously-normalized customer emails using saved mapping"""
	print(f"reverting {len(old_mapping)} customer emails to their previous state...")
	for customer in old_mapping:
		# if the email actually changed during normalization
		if customer[1] != customer[2]:
			# change it back to the old capitalization
			print(f"reverting {customer[0]} from {customer[2]} to {customer[1]}")
			stripe.Customer.modify(
				customer[0],
				email=customer[1]
			)


def generate_test_customers(quantity, verbose):
	"""populate stripe test account with a specified number of fake customers"""
	print(f"adding {quantity} fake customers to stripe test environment...")
	fake = Faker()  # generator object for fake data
	for _ in range(quantity):
		first = fake.first_name()
		last = fake.last_name()
		stripe.Customer.create(
			description="generated via script",
			name=f"{first} {last}",
			email=f"{first}.{last}@{fake.domain_name()}"
		)
		if verbose:
			print(f"name: {first} {last}, email: {first}.{last}@{fake.domain_name()}")
	return


def main(args):
	get_config()
	# if test data generation requested
	if args.testdata != 0:
		# first, verify the user is using the test api
		# (we don't want to ruin their actual customer data)
		if "sk_test_" not in stripe.api_key:
			raise Exception("You are operating on your live customer data. " +
							"Please insert your test API key instead.")
		generate_test_customers(args.testdata, args.verbose)
	elif args.revert:
		mapping = import_mapping(args.revert)
		revert_emails(mapping)
	else:
		email_mapping = normalize_emails(args.oversight, args.verbose, args.testmode)
		save_mapping(email_mapping)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog="Stripe Customer Email Normalizer",
		description="Converts existing customer emails to lowercase, " +
					"saves mapping of changes."
	)
	# by default, operate fully automatically, and don't print messages
	# regarding customers with no change
	parser.add_argument("-o", "--oversight", default=False, action="store_true",
						help="manually approve each customer data change")
	parser.add_argument("-v", "--verbose", default=False, action="store_true",
						help="print all operations to terminal")
	parser.add_argument("-td", "--testdata", type=int, default=0,
						help="amount of fake customers to generate")
	parser.add_argument("-tm", "--testmode", default=False, action="store_true",
						help="whether to write results to stripe or not")
	parser.add_argument("-r", "--revert", type=str, default=None,
						help="revert customer emails using a previous csv mapping")
	main(parser.parse_args())
