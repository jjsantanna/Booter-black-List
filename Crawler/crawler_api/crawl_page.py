import requests
import cfscrape
import tldextract # https://github.com/john-kurkowski/tldextract
from lxml import html
from crawler_api.booter_url import BooterURL

# hosts functionality and data relevant to crawling a single
# web page of a domain. This includes per-page properties like
# html content, headers and functionality to retrieve all 
# inbound and/or outbound URLs and per-category dictionary
# queries.
class CrawlPage:
	# constructor
	def __init__(this, response):
		this.URL     = BooterURL(response.url)
		this.HTML 	 = response.text
		this.Tree	 = html.fromstring(this.HTML)

		# create relative path for further URL queries 
		path = this.URL.Path
		if len(path) > 0 and path[0] =='/':
			this.RelativeURL = (this.URL.Hostname).replace('//', '/')			
		else:
			for i in reversed(path):
				if i == '/':
					break
				else:
					path = path[:-1]
			this.RelativeURL = (this.URL.Hostname + path).replace('//', '/')
		# print('relative:' + this.RelativeURL)

		# add a 'contains' list of URLs NOT to scrape
		this.Excludes = {
			'#',
			'mailto',
			'.pdf',
			'.doc',
			'.rar',
			'.zip',		
			'.png',
			'.jpeg',
			'.jpg',
			'.gif',
			'.bmp',
			'.atom',
			'.rss',	
			'skype:',
			'javascript:',
			'facebook',
			'twitter',
			'.tar.gz',
			'.exe',
			'.apk',
		}

	def URLLength(this):
		return len(this.URL.Hostname + this.URL.Path)

	def URLType(this):
		subdomains = tldextract.extract(this.URL.Hostname).subdomain
		subdomains = subdomains.split('.')
		# first remove exceptions from the list
		excludes = {
			'www',
			'ww1',
			'ww2',
			'',
		}
		for exclude in excludes:
			if exclude in subdomains:
				subdomains.remove(exclude)
		if len(subdomains) > 0: # if domain has subdomain, it is of type 2
			return 2
		else:
			return 1 # else we default to type 1. 
		# note: there is no way to check if a URL is of type 3 programatically; see discusson in thesis document

	def GetTopDomain(this):
		extract = tldextract.extract(this.URL.Hostname)
		return extract.domain + '.' + extract.suffix
		

	# returns all hyperlinks that point to inbound domains (relative paths = inbound)
	def GetInboundURLs(this):
		domain = this.URL.Hostname
		URLs = this.Tree.xpath('(//a)[contains(@href, "' + domain + '") or not(contains(@href, "http"))]/@href')

		urls_found = []
		result     = []
		for url in URLs:
			try:
				excluded = False
				for exclude in this.Excludes:
					if exclude in url.lower():
						excluded = True
						break
				if not excluded:	
					if domain in url:
						url = BooterURL(url)
						url = url.Hostname + url.Path
						if url[len(url) - 1] == '/':
							url = url[:-1]
						if url not in urls_found:
							result.append(url)
					else:		
						url = (this.RelativeURL + '/' + url).replace('//', '/')
						if url[len(url) - 1] == '/':
							url = url[:-1]
						if url not in urls_found:
							result.append(url)
					urls_found.append(url) # to check for duplicates
			except Exception as ex:
				pass

		return result

	# returns all outbound hyperlinks 
	def GetOutboundURLs(this):
		domain = this.URL.Hostname
		URLs = this.Tree.xpath('(//a)[contains(@href, "http") and not(contains(@href, "' + domain + '"))]/@href')


		urls_found = []
		result = []
		for url in URLs:
			excluded = False
			for exclude in this.Excludes:
				if exclude in url.lower():
					excluded = True
					break
			if not excluded:	
				if domain in url:
					if url not in urls_found:
						result.append(url)
				else:		
					if url not in urls_found:
						result.append(url)
				urls_found.append(url) # to check for duplicates
		return result


	# returns a tokenized list of words/phrases found in the crawled page's content
	def GetContent(this):
		text_content = []
		if len(this.HTML) < 250000: # don't run xPath on too large HTML pages, takes ages (slightly bias-ed but otherwise destroys crawler times)
			content      = this.Tree.xpath('(//p)[not(contains(@style, "hidden"))]/descendant-or-self::node()/text() | (//div)[not(contains(@style, "hidden"))]//descendant-or-self::node()[not(descendant-or-self::p) and not(descendant-or-self::script) and not (descendant-or-self::style)]/text()')
			for text in content:
				# first remove irelevant characters/symbols
				remove = { '\\t', '\\r', '\\n', '&nbsp;' }
				for removeable in remove:
					text = text.replace(removeable, '')
				# then split text by whitespace and add each entry to text_content
				text_content.append(text.split())

			# merge all lists in text_content list into one final list of words
			text_content = [item for sublist in text_content for item in sublist]
		else:
			# add bogus content to text_content (constant set as 1000)
			for i in range(0, 1000):
				text_content.append('too_large_html')

		return text_content

	# returns a bit-wise result whether this page contains an HTML login form (or register)
	def HasLoginForm(this):
		forms = this.Tree.xpath('(//form)//input[contains(@type, "password")]')
		return len(forms) > 0


	def __str__(this):
		return this.URL.Full_URL;
