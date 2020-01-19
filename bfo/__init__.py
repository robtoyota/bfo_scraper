import json
from bfo.scraper import Scraper
from bfo.fighter import Fighter
from bfo.prop import Prop
from bfo.mailgun import Mailgun


class BFOScraper:
	def __init__(self, config_path: str) -> None:
		self.CONFIG = self.get_config(config_path)  # Get config
		self.errors = []

		# Setup mailgun
		self.mailgun = Mailgun(
			email_domain=self.CONFIG['MAILGUN']['email_domain'],
			api_key=self.CONFIG['MAILGUN']['api_key']
		)

	# Run the program
	def run(self) -> bool:
		# Set the file locations
		json_file_fighters = "data/fighters.json"
		json_file_props = "data/props.json"

		# Reset any error messages
		self.errors = []

		# Get the DOM
		dom = None
		try:
			dom = Scraper.get_dom(self.CONFIG['SCRAPING']['url'], self.CONFIG['SCRAPING']['user_agent'])
			dom_error = ""
		except ValueError as e:
			dom_error = e

		# DOM is required
		if not dom:
			self.errors.append(
				f"Error: Cannot retrieve the HTML from {self.CONFIG['SCRAPING']['url']}."
				+ "Validate the URL in config.json."
				+ f"{dom_error}\n"
			)
			return False

		# Get the list of fighters and their props from the website
		dom_values = Scraper.scrape_data_from_dom(dom)

		# Get the list of fighters from the JSON file
		json_fighters = self.get_comparison_values_fom_json(json_file_fighters, 'fighter')
		json_props = self.get_comparison_values_fom_json(json_file_props, 'prop')

		# Compare the fighters
		fighter_messages = self.find_diffs(dom_values['fighters'], json_fighters)
		# Compare the props
		props_messages = self.find_diffs(dom_values['props'], json_props)

		# Generate the output message
		messages = []
		if len(fighter_messages):
			messages.append("Fighter changes:")
			messages += fighter_messages + []
		if len(props_messages):
			messages.append("Prop changes:")
			messages += props_messages + []

		# Email the results, if there are any messages to send
		if len(messages):
			email_content = "\n".join(messages)

			# Send the mail
			if self.mailgun.send_email(
					self.CONFIG['MAILGUN']['recipients'],
					"BFO Fighter Changes",
					email_content
			):
				# If the email was sent successfully, then write out the new DOM results to the json file
				self.write_json_file(json_file_fighters, dom_values['fighters'])
				self.write_json_file(json_file_props, dom_values['props'])
			else:  # Email failed to send
				self.errors.append(
					"Error: Email failed to send via Mailgun. Validate the values in config.json.\n"
					+ "These are the parameters:\n"
					+ f"email_domain = {self.CONFIG['MAILGUN']['email_domain']}."
					+ f"api_key = {self.CONFIG['MAILGUN']['api_key']}."
					+ f"recipients = {self.CONFIG['MAILGUN']['recipients']}."
					+ f"Message contents: {email_content}."
				)
				return False

		return True

	# Get the config values from the json file
	@staticmethod
	def get_config(file_name: str) -> dict:
		return BFOScraper.read_json(file_name)

	@staticmethod
	def read_json(file_path: str, create_file: bool = False) -> dict:
		# Default to an empty dict
		data = {}
		# Load the data from the json file
		try:
			with open(file_path) as json_file:
				data = json.load(json_file)
		except FileNotFoundError:  # If file does not exist, then create it
			if create_file:
				open(file_path, 'a').close()
		except json.decoder.JSONDecodeError:  # If the file is not a valid JSON file
			pass
		# Return the json values
		return data

	@staticmethod
	def write_json_file(json_file: str, dom_values: dict) -> None:
		json_output = []
		for data in dom_values.values():
			json_output.append(data.__dict__)

		with open(json_file, 'w') as f:
			json.dump(json_output, f)

	@staticmethod
	def get_comparison_values_fom_json(file_path: str, obj_type: str) -> dict:
		# Get the data from the .json file
		json_data = BFOScraper.read_json(file_path, create_file=True)

		# Populate the containing object instances
		output = {}
		for row in json_data:
			# Define the containing object
			if obj_type == "fighter":
				obj = Fighter()
			elif obj_type == "prop":
				obj = Prop()
			else:
				break

			# Load the json data into the object (all classes contain load_json)
			obj.load_json(row)
			output[obj.id] = obj  # Add the Fighter instance to the dict being returned

		return output

	@staticmethod
	def find_diffs(dom_data: dict, json_data: dict) -> list:
		messages = []
		for dom in dom_data.values():
			# only fighters have prop counts
			is_fighter = False
			if hasattr(dom, 'props'):
				is_fighter = True

			# Check if a new fighter or prop was added, and get the "original" value
			if dom.id in json_data:
				old = json_data[dom.id]
			else:
				if is_fighter:
					messages.append("New fighter added: %s; Props: %s." % (dom.name, dom.props))
					old = Fighter()
				else:
					messages.append("New prop added: %s;" % dom.name)
					old = Prop()

			# Compare the prop counts (only fighters have prop counts)
			if is_fighter:
				if dom.props != old.props:
					messages.append(
						"Props changed: %s - From %s to %s." %
						(dom.name, old.props, dom.props)
					)

			# Compare the sportsbooks to see if any new ones were added
			for sb_name, sb_val in dom.sports_books.items():
				if sb_name in old.sports_books:
					if sb_val != old.sports_books[sb_name]:
						# messages.append(
						# 	"Sportsbook changed: %s - %s: From %s to %s." %
						# 	(dom.name, sb_name, old.sportsbooks[sb_name], sb_val)
						# )
						pass
				else:
					messages.append(
						"Sportsbook added: %s - %s: %s." %
						(dom.name, sb_name, sb_val)
					)

		return messages
