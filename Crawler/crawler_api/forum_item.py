import datetime

# general purpose forum storage class 
# holds data of forum entires, including:
# title, link, text, age
# includes verification functions to check
# whether item potentially holds a Booter
class ForumItem:
	# constructor
	def __init__(this, title, url, date=None):
		this.Title = title
		this.URL   = url
		this.Date  = this.ParseDate(date)

	def ParseDate(this, date):
		date = date.lower()
		if "today" in date:
			return datetime.datetime.now()
		elif "yesterday" in date:
			return datetime.datetime.now() - datetime.timedelta(days=1)
		else:
			return datetime.datetime.strptime(date.lower(), '%m-%d-%Y %H:%M %p')

	# validates whether a forum entry "could" contain
	# a Booter e.g. by keyword search
	def IsPotentialBooter(this):
		keywords = { 
			"booter", 
			"stress", 
			"gbps",
			"down",
			"hitting",
			"boot"
		}
		treshold = 1
		found = 0
		for keyword in keywords:
			if keyword in this.Title.lower():
				found = found + 1

		return found >= treshold

	def __str__(this):
		return 'ForumItem: ' + this.Title[:31].ljust(31) + ' : ' + this.URL[30:] + ' |' + this.Date.strftime('%d-%m-%Y') + '|'

