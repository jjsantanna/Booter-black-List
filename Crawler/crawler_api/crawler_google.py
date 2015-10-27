import json
from crawler_api.crawler import Crawler


# documentation: https://developers.google.com/web-search/docs/#The_Basics

# this is the official API crawler of Google
# this sub-crawler is discontinuid as the maximum number of results is #64
# see crawler_google2 for the updated custom Google crawler.
class Crawler_Google(Crawler):
	'Crawler for Google\'s search API'
	def __init__(self, sleep_level=1):
		domain = 'https://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=8&userip=127.0.0.1' 
		Crawler.__init__(self, domain, sleep_level)
		self.PrintNote('CRAWLING GOOGLE')
		self.PrintDivider()
		self.Initialize()

	# overrides Crawler's crawl function
	def Crawl(self):
		keywords = ['Booters', 'DDOS', 'Stresser']
		       
		iterations = 8
		max_urls = iterations * 8 # API can only search 8 results at a time

		self.PrintUpdate('initiating crawling procedures: Google')
		self.PrintDivider()

		for keyword in keywords:
			for i in range(0, int(max_urls / 8)): # / 8 since API can only search 8 urls at a time
				# dynamically generate search query
				url = self.Target + "&q=" + keyword + "&start=" + str(i * 8)	
				self.PrintDebug('crawling: ' + "&q=" + keyword + "&start=" + str(i * 8))
				# read html and parse JSON
				response = self.Session.get(url, headers=self.Header)
				results = json.loads(response.text)
				# print(results)
				if results != None:            
					# now store all booters found in JSON to list of booters
					try:
						for result in results['responseData']['results']:
							self.AddToList(result['url'])
					except Exception as ex:
						self.PrintError('EXCEPTION: ' + str(ex))
						print(response.text)
		    
		self.PrintUpdate('DONE; found ' + str(len(self.URLs)) + ' potential Booters')
		self.PrintDivider()