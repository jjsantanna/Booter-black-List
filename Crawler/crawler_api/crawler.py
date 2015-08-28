import requests
import datetime
import cfscrape
import pythonwhois # https://github.com/joepie91/python-whois
import signal
from lxml import etree
from colorama import Fore, Back, Style
from random import choice, random
from time import sleep
from urllib.parse import urlparse
from crawler_api.booter_url import BooterURL
from crawler_api.crawl_page import CrawlPage
import crawler_api.storage



class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)


class Crawler:
	'General purpose Crawler; hosts functionality relevant to crawling a '
	'multitude of online web applications like forums, video-platforms and '
	'social media. The Crawler is not operable by itthis, but acts as a '
	'superclass for specific crawler instances per web application.'
	def __init__(this, target, sleep_level=1):
		this.Target = target
		this.Sleep_Level = sleep_level
		this.URLs = []
		
		this.Excludes = {
			'youtube.com',
			'gyazo.com',
			'dropbox.com',
			'uploading.com',
			'ge.tt',
			'rapidshare.com',
			'facebook.com',
			'twitter.com',
			'hackforums.net',
			'imgur.net',
			'imgur.com',
			'mediafire.com',
			'prntscr.com',
			'pastebin.com',
			'wikipedia',
			# 'gui', # not too sure about this, gui booters are known as software booters, any other chance of gui appearing in legit booter?
		}

		this.ParkPhrases = {
			"this domain may be for sale", 
			"this domain is for sale", 
			"buy this domain", 
			"this web page is parked", 
			"this domain name expired on", 
			"backorder this domain", 
			"this domain is available through",
		}

	# =========================================================================
	# INITIALIZATION
	# =========================================================================
	# Configures all connection objects and optionally logs into the service
	def Initialize(this):
		this.PrintUpdate('initiating crawling procedures')
		this.PrintDivider()
		this.Session = requests.Session()		
		# configure http header for each request
		user_agents = [ # you'll want to update this from time to time with newest user-agent headers (otherwise crawler could get detected)
		    # 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
		    # 'Opera/9.25 (Windows NT 5.1; U; en)',
		    # 'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
		    # 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
		    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
		] 
		this.Header = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
			'Accept-Encoding': 'gzip, deflate, sdch',
			'Accept-Language' : 'nl-NL,nl;q=0.8,en-US;q=0.6,en;q=0.4',
			'Cache-Control' : 'max-age=0',
			'Connection': 'keep-alive',
		    'User-Agent': choice(user_agents),
		}
		this.PrintDebug(str(this.Header))



	# Follows login procedures to initiate a session object per web application
	def Login(this, url, succes_page, post_data={}):
		this.PrintDivider()
		this.PrintUpdate('attempting to login at: ' + url)
		this.PrintDivider()

		response = this.Session.post(url, data=post_data, headers=this.Header)
		js_scraper = cfscrape.create_scraper()
		# response = js_scraper.post(url, headers=this.Header, data=post_data, timeout=15.0) 
		redirect_count = 1
		while 'HackForums.net has enabled additional security.' in response.text: # zou niet mogen voorkomen; requests regelt re-directs automatisch
			print('redirect!')
			# response = js_scraper.post(response.url, headers=this.Header, data=post_data,  timeout=15.0) 
			response = this.Session.post(url, data=post_data, headers=this.Header)
			redirect_count = redirect_count + 1
			if redirect_count == 1000: # increase to 5000, seemed to work last time?
				this.PrintError('REDIRECT COUNT OF 5 REACHED! ' + response.url)
				break

		print(response.url + ' | ' + succes_page)
		print(response.history)
		if response.url == succes_page:
			this.PrintUpdate('login succesful')
			this.PrintDivider()
			return True
		else:
			this.PrintError('failed to login to target server. Is the target online or blocked?')
			# print(response.text)
			return False

	# Adds a list of url substrings thst should be excluded from list of URLs
	def AddExcludes(this, excludes):
		this.Excludes = excludes


	# =========================================================================
	# CRAWL
	# =========================================================================
	# Crawls the web service, should be overriden in each subclass
	def Crawl(this, max_date):
		this.PrintError('Crawler.Crawl function not instantiated!')

	# Determines whether the url should be excluded
	def IsExcluded(this, URL):
		for excluded in this.Excludes:
			if excluded in URL.Full_URL:
				# print('EXCLUDED: ' + URL.UniqueName())
				return True
		return False

    # Adds a URL to the final URL list if it meets all conditions
	def AddToList(this, URL, source='?'):
		if not this.IsDuplicate(URL) and not this.IsExcluded(URL):
			try:
				# get status/respnse-code and resolved-url of URL
				status = this.GetStatus(URL.Full_URL)
				URL    = BooterURL(status[2])
				# save in database
				crawler_api.storage.SaveURL(URL, source, status[0])
				# then save in list if proper response or post error
				if status[1] == 200 or status[1] == 403 or status[1] == 202:
					BooterURL.Status = status # add status to URL for later use
					this.URLs.append(URL)
					this.PrintLine('CRAWLER: ' + URL.Full_URL, Fore.BLUE)
					if status[1] == 403 or status[1] == 202:
						print('Website blocked crawler; manually verify!')
				else:
					this.PrintNote('incorrect response code [' + str(status[1]) + ']: ' + URL.Full_URL)
			except Exception as ex:
				this.PrintError('EXCEPTION: ' + str(ex))


    # Determines whether a url is already added to the URL list
	def IsDuplicate(this, URL):
		for i in range(len(this.URLs)):
			if this.URLs[i].UniqueName() == URL.UniqueName():
				# print(this.URLs[i].UniqueName() + ' == ' + URL.UniqueName())
				return True

		return False

    # Finish crawling and output URL list to file
	def Finish(this, output_file):
		this.PrintUpdate('writing output to file \'' + output_file + '\'')
		f = open(output_file, 'w')
		for URL in this.URLs:
		    f.write(URL.UniqueName() + '\n')
		this.PrintUpdate('FINISHED; closing operations')
		this.PrintDivider()
		return this.URLs

	# sleeps for a semi-random amount of time to mitigate bot detection
	def Sleep(this):
		sleep(this.Sleep_Level + random() * this.Sleep_Level)

	# enables javascript to circumvent cloudflare's bot detection
	def JSCrawl(this, url):
		js_scraper = cfscrape.create_scraper()
		response = js_scraper.get(url, headers=this.Header, timeout=15.0) 
		redirect_count = 0
		while 'http-equiv="Refresh"' in response.text: 
			response = js_scraper.get(response.url, headers=this.Header, timeout=15.0) 
			redirect_count = redirect_count + 1
			if redirect_count == 5:
				this.PrintError('REDIRECT COUNT OF 5 REACHED! ' + response.url)
				break
		return response

	# retrieves status of website: resolves URL, response code and whether it
	# is offline/online or for sale
	def GetStatus(this, url):
		response = this.JSCrawl(url)
		# response = this.Session.get(url, headers=this.Header)
		if response.status_code == 200 or response.status_code == 403 or response.status_code == 202:
			# check if for sale, otherwise site deemed as online
			for phrase in this.ParkPhrases:
				if phrase in response.text.lower():
					return ('free', response.status_code, response.url)
			# else site is online
			return ('on', response.status_code, response.url)				
		else:
			return ('off', response.status_code, response.url)

	# =========================================================================
	# EVIDENCE AND HEURISTICS
	# =========================================================================
	# scrapes a (potential) Booter URL for evidence as reported by Booter 
	# characteristics in 'Improving the Dynamic Booter (black)list generation'
	def Scrape(this, URL, days_update=0):
		# Check if number of days_update days have passed since last update, and if so, update
		if crawler_api.storage.RowExists('test_scores3', URL.UniqueName()): 
			last_update  = crawler_api.storage.GetSingleValue('test_scores3', URL.UniqueName(), 'lastUpdate')
			last_update  = datetime.datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')
			# print(last_update)
			current_date = datetime.datetime.now()
			difference   = (current_date - last_update).days
			if difference < days_update:
				this.PrintDivider()
				this.PrintDebug('Skip scrape: ' + URL.UniqueName() + '; last scraped: ' + str(last_update))
				return 
		# Else, start scraping
		try:
			this.PrintDivider()
			this.PrintDebug('STARTING SCRAPE: ' + URL.Full_URL)
			### 1. structure characteristics
			this.PrintDivider()
			this.PrintUpdate('obtaining structure-based characteristics')
			this.PrintDivider()
			# - 1.1 number of pages
			number_of_pages 	= -1.0
			number_of_pages_raw = -1.0 # also store a raw score for data analysis 
			# crawl through the URL and each subsequent inbound URL 
			crawled     = []
			crawl_count = 0
			max_urls    = 50
			# - get landing page
			landing_page = CrawlPage(this.JSCrawl(URL.Full_URL))
			inbounds     = landing_page.GetInboundURLs()
			crash_pages  = []
			
			this.PrintNote('scraping: ' + URL.Full_URL)	
			page_url	 = (landing_page.URL.Hostname + landing_page.URL.Path).replace('//','/')
			if page_url[len(page_url) - 1] == '/':
				page_url = page_url[:-1]
			depth_levels = { page_url : 0 }
			inbounds.append(page_url)

			# 1.1.1 store depth levels of landing page found inbound urls
			for inbound in inbounds:
				if inbound not in URL.Full_URL and inbound not in page_url:
					depth_levels[inbound] = 1

			crawled.append(landing_page)

			# 1.1.2. then from each found (inbound) URL, keep crawling until
			fail_loop_attempts = 0		
			while crawl_count < len(inbounds) and crawl_count < max_urls - 1:
				inbound = inbounds[crawl_count]
				if inbound not in crawled and inbound not in crash_pages:
					try:
						with timeout(seconds=20):
							# crawl next page and obtain new inbound/outbound urls
							this.PrintNote('scraping: ' + 'http://' + inbound)
							
							response = this.JSCrawl('http://' + inbound)
							crawl_page    = CrawlPage(response)
							new_inbounds  = crawl_page.GetInboundURLs()
							# for each of the new_inbounds, set their depth level if less than currently stored (or not yet stored)
							for new_inbound in new_inbounds:
								if new_inbound not in depth_levels:
									depth_levels[new_inbound] = depth_levels[inbound] + 1
							# merge results
							inbounds  = inbounds  + list(set(new_inbounds)  - set(inbounds))
							# then continue
							crawled.append(crawl_page)
							crawl_count = crawl_count + 1
					except Exception as ex:
						this.PrintError('EXCEPTION: ' + str(ex))
						crash_pages.append(inbound)
						crawl_count = crawl_count + 1
				else:
					fail_loop_attempts += 1 # aborts loop after 10000 tries; indicating infinite loop
					if fail_loop_attempts > 10000:
						this.PrintError('INFINITE LOOP detected; aborting scrape')
						break

		
			# 1.1.3 calculate scores
			# use quadratic equation (to give numbers with low pages higher scores)
			# equation: y = -2x^2 + 1 ... (y=0) = 0.707
			# with 25 pages, score is 0.75, so first half pages give 1/4 drop-down in score
			number_of_pages_raw = len(inbounds)
			if number_of_pages_raw > 0:
				number_of_pages = -2 * (number_of_pages_raw / (50/0.707106781	)) ** 2 + 1
				number_of_pages = max(number_of_pages, 0.0) 
			this.PrintUpdate('number of pages: ' + str(number_of_pages_raw))

			# - 1.2. URL type
			# how to determine its url type? difficult to determine programmaticaly 
			# can check if contains subdomain other than www/ww1/ww2 etc.	
			url_type_raw = landing_page.URLType()
			if url_type_raw == 2:
				url_type = 0.0
			else:
				url_type = 1.0
			this.PrintUpdate('url type: ' + str(url_type_raw))

			# - 1.3. Average depth level
			# take previously retrieved depth levels and take average
			average_depth_level     = 0.0
			average_depth_level_raw = 0.0
			for depth_url in depth_levels:
				average_depth_level_raw = average_depth_level_raw + depth_levels[depth_url]
			# calculate score: take linear value between 1.0 and 3.0
			average_depth_level_raw = average_depth_level_raw / len(depth_levels)
			if average_depth_level_raw <= 1.0:
				average_depth_level = 1.0
			else:
				average_depth_level = max(1.0 - ((average_depth_level_raw - 1.0) / 2.0), 0.0)
			this.PrintUpdate('average depth level: ' + str(average_depth_level_raw))

			# - 1.4. Average URL length
			average_url_length     = -1.0
			average_url_length_raw = -1.0
			for page in inbounds: # use inbounds, not pages crawled as they give much more results
				average_url_length_raw = average_url_length_raw + len(page)
			# calculate score: interpolate linearly from lowest occurence to highest Booter occurence
			# at the moment between 15 - 30
			average_url_length_raw = average_url_length_raw / len(inbounds) 
			if average_url_length_raw <= 15:
				average_url_length = 1.0
			else:
				average_url_length = max(1.0 - ((average_url_length_raw - 15) / 15), 0.0)
			this.PrintUpdate('average url length: ' + str(average_url_length_raw))


			### 2. content-based characteristics
			# note for DNS stuff: use ldns; Roland approves
			this.PrintDivider()
			this.PrintUpdate('obtaining content-based characteristics')
			this.PrintDivider()


			# get whois information
			# "Each part represents the response from a specific WHOIS server. Because the WHOIS doesn't force WHOIS 
			# servers to follow a unique response layout, each server needs its own dedicated parser."
			domain_age                      = -1.0
			domain_age_raw                  = -1.0
			domain_reservation_duration     = -1.0
			domain_reservation_duration_raw = -1.0
			try:
				with timeout(seconds=10):
					whois = pythonwhois.get_whois(landing_page.GetTopDomain(), False) # http://cryto.net/pythonwhois/usage.html
			except Exception as ex:
				this.PrintError('EXCEPTION: get WHOIS data: ' + str(ex))
			try:
				# - 2.1. Domain age
				current_date    = datetime.datetime.today()
				date_registered = whois['creation_date'][0]
				domain_age_raw	= (current_date - date_registered).days
				# calculate score: linear interpolation between current_date and first occurence of 
				# booter in data: 2011
				days_since_first = (current_date - datetime.datetime(2011, 10, 28)).days
				domain_age = max(1.0 - (domain_age_raw / days_since_first), 0.0)
				this.PrintUpdate('domain age: ' + str(domain_age_raw))
			except Exception as ex:
				this.PrintError('EXCEPTION: whois keywords, likely registrar: ' + str(ex))

			try:
				# - 2.2 Domain reservation duration
				current_date  				    = datetime.datetime.today()
				expire_date    			        = whois['expiration_date'][0]
				domain_reservation_duration_raw = (expire_date - current_date).days
				# calculate score: between 1 - 2 years; < 1 year = 1.0
				if domain_reservation_duration_raw < 183:
					domain_reservation_duration = 1.0
				else:
					# domain_reservation_duration = max(1.0 - ((domain_reservation_duration_raw - 365) / 365), 0.0)
					domain_reservation_duration = max(1.0 - (domain_reservation_duration_raw - 183) / 182, 0.0)
				this.PrintUpdate('domain reservation duration: ' + str(domain_reservation_duration_raw))
			except Exception as ex:
				this.PrintError('EXCEPTION: whois keywords, likely registrar: ' + str(ex))

			# - 2.3. WHOIS private
			# there doesn't exist a private WHOIS field, but private information can be obtained through
			# heuristics using common phrases found by privacy-replacing registry information.
			try:
				private_phrases = [
					'whoisguard',
					'whoisprotect',
					'domainsbyproxy',
					# 'whoisprivacyprotect', # are caught by privacy term anyways
					'protecteddomainservices',
					# 'myprivacy',
					# 'whoisprivacycorp',
					# 'privacyprotect',
					'namecheap',
					'privacy',
					'private',
				]
				whois_private = 0.0
				reg_name 	  = whois['contacts']['registrant']['name'].lower()
				reg_email 	  = whois['contacts']['registrant']['email'].lower()
				for phrase in private_phrases:
					if phrase in reg_name or phrase in reg_email: #or phrase in reg_org :
						whois_private = 1.0
						break
			except Exception as ex:
				this.PrintError('EXCEPTION: whois keyfields, private set to -1.0: ' + str(ex))
				whois_private = -1.0
			this.PrintUpdate('WHOIS private: ' + str(whois_private))

			# - 2.4. DPS
			# similar to whois private, use heuristics to determine whether website uses DPS,
			# first we try to determine whether it uses DNS based DPS by checking nameservers
			try:
				with timeout(seconds=10):
					dps_names = [
						'cloudflare',
						'incapsula',
						'prolexic',
						'akamai',
						'verisign',
						'blazingfast',
					]
					dps = 0.0
					if 'nameservers' in whois:
						for nameserver in whois['nameservers']:
							if dps == 0.0:
								for dps_name in dps_names:
									if dps_name in nameserver.lower():
										dps = 1.0
										break
					# if nothing found from nameservers, also check redirection history if dps redirect page was used
					if dps < 0.5:
						response_text = this.Session.post(URL.Full_URL, headers=this.Header, allow_redirects=False).text
						this.PrintNote('No DPS detected from NS; checking re-direction history')
						for dps_name in dps_names:
							if dps_name in response_text:
								dps = 1.0
			except Exception as ex:
				this.PrintError('EXCEPTION: dps set to -1.0: ' + str(ex))
				dps = -1.0
			this.PrintUpdate('DPS: ' + str(dps))

			# - 2.5. Page rank
			try:
				url           = 'http://data.alexa.com/data?cli=10&dat=s&url=' + URL.Hostname
				response      = this.Session.get(url)
				tree 	      = etree.XML(response.text.encode('utf-8'))
				page_rank_raw = tree.xpath('(//REACH)/@RANK')[0]
				page_rank     = 0.0
				if int(page_rank_raw) > 200000: # determined from highest booter (ipstresser.com - vdos-s.com) minus offset
					page_rank = 1.0
			except Exception as ex:
				page_rank_raw = 25426978.0 # set to highest occuring page rank (lower than that if non-existent)
				page_rank = 1.0

			this.PrintUpdate('Page rank: ' + str(page_rank_raw))

			
			### 3. host-based characteristics
			this.PrintDivider()
			this.PrintUpdate('obtaining host-based characteristics')
			this.PrintDivider()

			# - 3.1. Average content size
			average_content_size     = 0.0
			average_content_size_raw = 0.0
			crawl_contents = []
			for crawl_page in crawled:
				crawl_content = crawl_page.GetContent();
				crawl_contents.append(crawl_content)
				average_content_size_raw = average_content_size_raw + len(crawl_content)
			average_content_size_raw = average_content_size_raw / len(crawled)
			# calculte score: linear interpolation between 50 - (avg_max_booter = 250)
			if average_content_size_raw < 50:
				average_content_size = 1.0
			else:
				average_content_size = max(1.0 - (average_content_size_raw - 50) / 200, 0.0)
			this.PrintUpdate('Average content size: ' + str(average_content_size_raw))

			# - 3.2. Outbound hyperlinks
			outbound_hyperlinks     = 0.0
			outbound_hyperlinks_raw = 0.0
			for crawl_page in crawled:
				outbound_hyperlinks_raw = outbound_hyperlinks_raw + len(crawl_page.GetOutboundURLs())
			outbound_hyperlinks_raw = outbound_hyperlinks_raw / len(crawled)
			# calculate score: linear interpolation between 0 and 2
			outbound_hyperlinks = max(1.0 - outbound_hyperlinks_raw / 2.0, 0.0)
			this.PrintUpdate('Average outbound hyperlinks: ' + str(outbound_hyperlinks_raw))

			# - 3.3. Category-specific dictionary
			dictionary = [ 'stress', 'booter', 'ddos', 'powerful', 'resolver', 'price' ] # or pric, so we can also get items like pricing
			category_specific_dictionary     = 0.0
			category_specific_dictionary_raw = 0.0
			words = landing_page.GetContent()
			for item in dictionary:
				for word in words:
					if item in word.lower():
						category_specific_dictionary_raw = category_specific_dictionary_raw + 1
			# - now calculate percentage of these words occuring relative to total page content
			if len(words) > 0:
				category_specific_dictionary_raw = category_specific_dictionary_raw / len(words)
			else:
				category_specific_dictionary_raw = 0.0
			# calculate score: interpolate between 0.00 and 0.05
			category_specific_dictionary = min(category_specific_dictionary_raw / 0.05, 1.0)
			this.PrintUpdate('Category specific dictionary: ' + str(category_specific_dictionary_raw))

			# - 3.4. Resolver indication (only the landing page)
			resolver_indication = 0.0
			dictionary = [ 'skype' , 'xbox', 'resolve', 'cloudflare' ]
			for item in dictionary:
				for word in words:
					if item in word.lower():
						resolver_indication = 1.0
			this.PrintUpdate('Resolver indication: ' + str(resolver_indication))

			# - 3.5. Terms of Services page
			terms_of_services_page = 0.0
			# - check if one of the urls contains tos or terms and service
			for url in inbounds:
				url = url.lower();
				if '/tos' in url or 'terms' in url and 'service' in url:
					terms_of_services_page = 1.0
			# - if not yet found, also check for content hints in all the pages
			tos_phrases = [
				'terms and conditions', 
				'purposes intended', 
				'you are responsible', 
				'we have the right', 
				'terms of service',
				'understand and agree',
			]
			if terms_of_services_page < 0.5:
				for content in crawl_contents:
					text = ' '.join(content).lower()
					# for page in crawled:
					# text = ' '.join(page.GetContent()).lower()
					for phrase in tos_phrases:
						if phrase in text:
							terms_of_services_page = 1.0
							break
					if terms_of_services_page > 0.5:
						break
			this.PrintUpdate('Terms of services page: ' + str(terms_of_services_page))

			# - 3.6. Login-form depth level
			# this does also take into account register forms, but that's generally expected
			# to be on the same level as login forms so not an issue
			login_form_depth_level     = -1.0
			login_form_depth_level_raw =  3.0 # set to max found in dataset if non-existent
			forms_urls = []
			for page in crawled:
				if page.HasLoginForm(): 
					page_url = page.URL.Hostname + page.URL.Path + page.URL.Query
					if page_url[len(page_url) - 1] == '/':
						page_url = page_url[:-1]
					forms_urls.append(page_url)
			# print(forms_urls)
			# print(depth_levels)
			min_depth = 100
			for url in forms_urls:
				for depth_url in depth_levels:
					if depth_url == url:
						if depth_levels[url] < min_depth:
							min_depth = depth_levels[url]
						break
			if min_depth != 100:
				login_form_depth_level_raw = min_depth
				# transform to score (if depth level exceeds 2, score becomes 0)
			login_form_depth_level = min(max(1.0 - min_depth * 0.5, 0.0), 1.0)
			this.PrintUpdate('Login-form depth level: ' + str(login_form_depth_level_raw))

			### 4. Now save the results into the database
			crawler_api.storage.SaveScore('test_scores3',
				URL,
				datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				number_of_pages,
				url_type,
				average_depth_level,
				average_url_length,
				domain_age,
				domain_reservation_duration,
				whois_private,
				dps,
				page_rank,
				average_content_size,
				outbound_hyperlinks,
				category_specific_dictionary,
				resolver_indication,
				terms_of_services_page,
				login_form_depth_level
			)
			# crawler_api.storage.SaveScore('characteristics',
			# 	URL,
			# 	datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
			# 	number_of_pages_raw,
			# 	url_type_raw,
			# 	average_depth_level_raw,
			# 	average_url_length_raw,
			# 	domain_age_raw,
			# 	domain_reservation_duration_raw,
			# 	whois_private,
			# 	dps,
			# 	page_rank_raw,
			# 	average_content_size_raw,
			# 	outbound_hyperlinks_raw,
			# 	category_specific_dictionary_raw,
			# 	resolver_indication,
			# 	terms_of_services_page,
			# 	login_form_depth_level_raw
			# )
			this.Sleep()

		except Exception as ex:
			this.PrintError('EXCEPTION: Scrape failed: connection host ' + str(ex))
			# raise



	# =========================================================================
	# PRINT FUNCTIONALITY
	# =========================================================================
	def PrintLine(this, text, color=Fore.WHITE, style=Style.NORMAL):
		print(color + style + text[:80] + Style.RESET_ALL)
	def PrintDivider(this):
		this.PrintLine('................................................................................', Fore.YELLOW)
	def PrintUpdate(this, text):
		this.PrintLine('CRAWLER: ' + text, Fore.GREEN)
	def PrintError(this, text):
		this.PrintLine('CRAWLER: ' + text, Fore.RED)
	def PrintDebug(this, text):
		this.PrintLine('CRAWLER: ' + text, Fore.CYAN)
	def PrintNote(this, text):
		this.PrintLine('CRAWLER: ' + text, Fore.WHITE, Style.DIM)

	