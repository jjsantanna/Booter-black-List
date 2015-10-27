import json
import re
from lxml import html
from crawler_api.crawler import Crawler
from colorama import Fore, Back, Style
from crawler_api.booter_url import BooterURL

class Crawler_Youtube(Crawler):
	'Crawler of Youtube via default web requests'
	def __init__(this, sleep_level=1):
		domain = 'https://www.youtube.com/results?' 
		Crawler.__init__(this, domain, sleep_level)

		this.PrintNote('CRAWLING YOUTUBE')
		this.PrintDivider()
		this.Initialize()

	# def Login(this):
		# no login
		# this.PrintError('NO LOGIN REQUIRED')

	# overrides Crawler's crawl function
	def Crawl(this, max_results=100):
		keywords = ['online booter', 'stresser', 'ddoser']

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
					response = this.JSCrawl(url)
					tree 	 = html.fromstring(response.text) 
					split   = 10

					urls_found = []

					descriptions = tree.xpath('(//div)[contains(@class, "yt-lockup-description")]/descendant-or-self::*/text()')					
					for description in descriptions:
						# check whether description certainly doesn't hold an online booter
						if this.StopSearching(description):
							continue

						# find all urls in description
						urls = re.findall('http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', description)
						for url in urls:
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
	# certain stop keywords are found like 'tutorial'
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
