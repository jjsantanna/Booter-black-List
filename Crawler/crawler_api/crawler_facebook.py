import json
import re
from lxml import html
from crawler_api.crawler import Crawler
from colorama import Fore, Back, Style
from crawler_api.booter_url import BooterURL

# documentation: https://developers.google.com/web-search/docs/#The_Basics

# this sub-crawler is discontinuid; Facebook unreliably queries/blocks results
class Crawler_Facebook(Crawler):
	'Crawler of Facebook via default web requests'
	def __init__(this, sleep_level=1):
		domain = 'https://www.facebook.com' 
		Crawler.__init__(this, domain, sleep_level)

		this.PrintNote('CRAWLING FACEBOOK')
		this.PrintDivider()
		this.Initialize()

	# login to facebook.com
	def Login(this):
		username = 'your_username_here'
		password = 'your_password_here'
		url = this.Target + '/login.php?login_attempt=1'
		post_data = {
			'email': username,
			'pass': password,
			'lsd': 'AVo9nkyx',
			'display': '',
			'enable_profile_selector': '',
			'legacy_return': '1',
			'profile_selector_ids': '',
			'trynum': '1',
			'timezone': '-120',
			'lgndim': 'eyJ3IjoxOTIwLCJoIjoxMjAwLCJhdyI6MTkyMCwiYWgiOjExNzYsImMiOjI0fQ==',
    		'lgnrnd': '011014_jFmL',
    		'default_persistent': '0',
    		'qsstamp': 'W1tbMzMsMzgsNDMsNTgsNzcsODMsOTcsMTA2LDEyOCwxMzAsMTM1LDEzNiwxNTQsMTYxLDE2MiwxNzUsMTc5LDIwMCwyMDYsMjQyLDI1NiwzMDQsMzEwLDMxMSwzMTMsMzE5LDMzOSwzNDgsMzg4LDM5NiwzOTksNDIwLDQyNCw0NDMsNDcxLDQ4MSw0OTQsNTM3LDU1NSw1NzEsNzAyLDczMV1dLCJBWm5OdlBDQ0RQbHluRUloVUFfa1REaWFVZnJ3MnhaWWZoUjVvWXk4SEFtUEhCSHpIMmx1Z2VneUZxWDRqRTZWaUtXblZtQVlmRGZTeXY2UFY3OTdiajROTkxvd0RpVUtzYXhveXY4M3IycWlBSzJpZWNIeTU0UEs1UGFOZFpXanhxRTI1b3JDUG5vR0pidjFsZ2xUcnBrcFhGaktQODlmd1VNUGNUYkM3VkdsOWY2T0hTb3BTT0hGQ3pIUkF6MElFZFNESFlnclVpX2ZpeFFhOE13SkhMZV9KNUliTUo4dEFKeFVJVDkyaXoxZ0ZBIl0=',
		}
		return super(Crawler_Facebook, this).Login(
			url, 
			this.Target, 
			post_data
		)

	# overrides Crawler's crawl function
	def Crawl(this, max_results=100):
		keywords = ['online booter', 'stresser']

		nr_pages = int(max_results / 10)

		this.PrintUpdate('initiating crawling procedures: Youtube')

		for keyword in keywords:
			this.PrintDivider()
			this.PrintNote('KEYWORD: ' + keyword)
			for i in range(0, nr_pages): 
				counter = 0
				try:
					# dynamically generate search query
					query =  '&search_query="' + keyword	+ '"&page=' + str(i)
					url = this.Target + query
					this.PrintDivider()
					this.PrintDebug('crawling: ' + query) 
					# read html and parse JSON
					# response = this.Session.get(url, headers=this.Header)
					response = this.JSCrawl(url)
					# print(response.text)
					tree 	 = html.fromstring(response.text) 
					split   = 10

					urls_found = []

					# urls = tree.xpath('(//li)[@class="g"]//a[not(contains(@href, "translate"))]/text()')
					descriptions = tree.xpath('(//div)[contains(@class, "yt-lockup-description")]/descendant-or-self::*/text()')					
					for description in descriptions:
						# check whether description certainly doesn't hold an online booter
						if this.StopSearching(description):
							continue

						# find all urls in description
						urls = re.findall('http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', description)
						for url in urls:
							# url = ''.join(map(str, url))
							urls_found.append(url)

						
					# also check for explicit urls in descriptions
					urls = tree.xpath('(//div)[contains(@class, "yt-lockup-description")]//a/@href')					
					for url in urls:
						if url not in urls_found:
							urls_found.append(url)

					this.PrintDivider()
					this.PrintUpdate('obtained ' + str(len(urls_found)) + ' potential URLs; extracting...')
					this.PrintDivider()

					# resolve each url and add returned url to final urls
					for url in urls_found:
						this.AddToList(BooterURL(url), 'Youtube')
						counter = counter + 1
						if counter % split == 0:
							this.PrintDivider()	

					this.Sleep()
				except Exception as ex:
					this.PrintError('EXCEPTION: ' + str(ex))
					this.Sleep()

		this.PrintUpdate('DONE; found ' + str(len(this.URLs)) + ' potential Booters')
		this.PrintDivider()


	# decides to stop crawling a specific description as soon as
	# certain stop keywords are found like 'download'
	def StopSearching(this, description):
		stop_words = {
			'tutorial'
			'download:'
			'gui',
			'dekstop'
		}
		text = description.lower()
		for word in stop_words:
			if word in text:
				return True

		return False
