from bs4 import BeautifulSoup
import requests
import re
from bfo.fighter import Fighter
from bfo.prop import Prop


class Scraper:
	def __init__(self):
		pass

	# Get the DOM of the web page
	@staticmethod
	def get_dom(url: str, user_agent: str = None) -> BeautifulSoup:
		# Simulate a browser
		if not user_agent:
			user_agent = "Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0"

		# Set the headers
		headers = {
			'User-Agent': user_agent
		}

		# Get the HTML of the page
		page = requests.get(url, headers=headers, verify=False)

		# Make sure the status response is good
		if page.status_code != 200:  # Was there a problem getting the page?
			error_message = f"Error reading the page (status {page.status_code}): {url}"
			raise ValueError(error_message)

		# Return the DOM
		return BeautifulSoup(page.content, "html.parser")

	# Get the list of fighters and their propositional bets
	@staticmethod
	def scrape_data_from_dom(dom: BeautifulSoup) -> dict:
		fighters = {}
		props = {}
		fighter_ids = []

		# Loop through the fights
		fight_tables = dom.find_all("table", class_="odds-table")
		for fight_table in fight_tables:  # Loop through the different fight tables
			sports_books_names = Scraper.extract_sports_book_names_from_dom(fight_table)
			# Loop through each fighter and set of props
			css_classes_fighter = ['odd', 'even']
			css_classes_prop = ['pr', 'pr-odd']

			# Loop through each row in the fight table
			for dom in fight_table.find("tbody").find_all("tr", class_=css_classes_fighter + css_classes_prop):
				# Make sure this row has <td> elements, and isn't just the "odds-table-responsive-header"
				if len(dom.find_all("td")) == 0:
					continue

				sports_books = Scraper.extract_sports_book_values(dom, sports_books_names)

				# If the dom element is for fighters, then load the fighter
				if [i for i in dom['class'] if i in css_classes_fighter]:  # Loop through element's classes
					f = Fighter()
					f.load_dom(dom, sports_books)
					fighters[f.id] = f  # Add the Fighter instance to the dict being returned
					fighter_ids.append(f.id)

				# If the dom element is for props, then load the props
				elif [i for i in dom['class'] if i in css_classes_prop]:  # Loop through element's classes
					p = Prop()
					p.load_dom(dom, sports_books, fighters[fighter_ids[-1]], fighters[fighter_ids[-2]])
					props[p.id] = p  # Add the Prop instance to the dict being returned

		return {'fighters': fighters, 'props': props}

	# Get the name of the sports_books from the column headers
	@staticmethod
	def extract_sports_book_names_from_dom(dom: BeautifulSoup) -> list:
		sports_books = []
		# Loop through the header row
		for th in dom.find("thead").find_all("th"):
			# Get the name of the column header
			try:
				name = th.find("a").text
			except AttributeError:
				continue  # No text found

			# Ignore headers that we don't care about
			if name in ["", "Props"]:
				continue

			# Get the headers that were not filtered out:
			sports_books.append(name)

		return sports_books

	# Extract the sports book values for each sports book name
	@staticmethod
	def extract_sports_book_values(dom: BeautifulSoup, sports_books_names: list) -> dict:
		i = 0
		sports_books = {}

		# Loop through each column
		for td in dom.find_all("td"):
			# Get the sports book container span
			sb = td.find("span", id=re.compile('^oID'))  # Identify the span by an ID that starts with oID#########
			# sb = td.find("span[id^=oID]")  # Identify the span by an ID that starts with oID#########
			if sb:
				# Exclude columns that we don't want
				try:
					# Check the class
					if sb.parent.parent.get("class")[0] in ["prop-cell", "button-cell"]:
						continue
				except TypeError:  # If there is no class, then keep going
					pass
				# Add the sports book value to the returned dict
				sports_books[sports_books_names[i]] = sb.text
			i += 1

		return sports_books
