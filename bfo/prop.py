from bs4 import BeautifulSoup
from bfo.fighter import Fighter


class Prop:
	def __init__(self) -> None:
		self.id = ""
		self.name = ""
		self.sports_books = {}

	def load_dom(self, dom: BeautifulSoup, sports_books: dict, fighter1: Fighter, fighter2: Fighter) -> None:
		self.name = fighter1.name + " vs " + fighter2.name + ": " + dom.find("th").text
		self.id = self.name
		self.sports_books = sports_books

	def load_json(self, json_data: dict) -> None:
		self.id = json_data['id']
		self.name = json_data['name']

		# Set the sports books
		for sb_name, sb_val in json_data['sports_books'].items():
			self.sports_books[sb_name] = sb_val
