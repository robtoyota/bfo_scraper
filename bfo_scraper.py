#!/usr/bin/python

from bfo import BFOScraper
import datetime
import time
import sys


def main(sleep_minutes: float) -> None:
	# Initialize the BFO Scraper
	bfo = BFOScraper('config.json')

	# Main program loop
	while True:
		error_message = ""  # Reset the error message before each run
		try:
			# Run the program
			bfo.run()
		except Exception as e:  # Ugh
			# Catch and email the error
			error_message = f"Exception thrown: {e}\n\nThe program will continue running, but please report the error."

		# Check for any error messages returned
		if len(bfo.errors):
			error_message += "\n\n".join(bfo.errors)

		# Email any errors returned by the run
		if error_message != '':
			print(error_message)
			bfo.mailgun.send_email(
				bfo.CONFIG['MAILGUN']['recipients'],
				"BFO Scraper - Program error",
				error_message
			)

		if sleep_minutes == -1:
			break  # If the sleep_minutes is -1, then don't loop
		else:
			# Output the run log
			print("Run - %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
			time.sleep(sleep_minutes * 60)  # Check again in X minutes


if __name__ == '__main__':
	# Accept the sleep minutes
	in_sleep_minutes = -1  # Default to end after a single run
	if len(sys.argv) > 1:
		try:
			in_sleep_minutes = float(sys.argv[1])
		except ValueError:
			pass

	main(in_sleep_minutes)
