import requests


class Mailgun:
	def __init__(self, email_domain: str, api_key: str) -> None:
		self.email_domain = email_domain
		self.api_key = api_key

	def send_email(self, recipients: list, subject: str, message: str) -> bool:
		try:
			requests.post(
				"https://api.mailgun.net/v3/" + self.email_domain + "/messages",
				auth=("api", self.api_key),
				data={
					"from": "BestFightOdds Scraper <mailgun@" + self.email_domain + ">",
					"to": recipients,
					"subject": subject,
					"text": message
				}
			)
			return True
		except Exception as e:
			print("Unable to send the notification email through mailgun!")
			print(f"Exception thrown: {e}")
			return False
