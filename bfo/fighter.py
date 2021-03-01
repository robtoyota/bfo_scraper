from bs4 import BeautifulSoup


class Fighter:
	def __init__(self) -> None:
		self.id = ""
		self.name = ""
		self.props = ""
		self.sports_books = {}

	def load_dom(self, dom: BeautifulSoup, sports_books: dict) -> None:
		self.id = dom.find("th").find("a")['href']
		self.name = dom.find("th").find("a").find("span").text
		self.set_props(dom.find("td", class_="prop-cell").text)
		self.sports_books = sports_books

	def load_json(self, json_data: dict) -> None:
		self.id = json_data['id']
		self.name = json_data['name']
		self.set_props(json_data['props'])

		# Set the sports books
		for sb_name, sb_val in json_data['sports_books'].items():
			self.sports_books[sb_name] = sb_val

	def set_props(self, props: str) -> None:  # Setter method for props
		# Default to 0
		props = str(props).strip()
		if not props.isdigit():
			props = "0"
		self.props = props
