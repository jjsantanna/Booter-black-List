from lxml import html
from colorama import Fore, Back, Style
from crawler_api.crawler import Crawler
from crawler_api.forum_item import ForumItem
from crawler_api.booter_url import BooterURL


class Crawler_Hackforums(Crawler):
	'Crawler for web services of www.hackforums.net'
	def __init__(self, sleep_level=1):
		domain = 'http://www.hackforums.net/' 
		Crawler.__init__(self, domain, sleep_level)

		# this.Excludes = {
		# 	'youtube.com',
		# 	'gyazo.com',
		# 	'dropbox.com',
		# 	'uploading.com',
		# 	'ge.tt',
		# 	'rapidshare.com',
		# 	'facebook.com',
		# 	'twitter.com',
		# 	'hackforums.net',
		# 	'imgur.net',
		# 	'mediafire.com',
		# 	'prntscr.com',
		# 	'pastebin.com',
		# 	'imgur.com',
		# }

		self.PrintNote('CRAWLING HACKFORUMS')
		self.PrintDivider()
		self.Initialize()

	# Login to hackforums.net
	# NOTE: This will not work everytime, you have to manually login to hackforums.net first as to 
	# circumvent their first-login IP check using the credentials below.
	def Login(self):
		username = 'SwagLordxx69' # username generated as the most non-suspicious username possible
		password = 'LePass1337'
		url = self.Target + 'member.php'
		post_data = {
			'username': username,
			'password': password,
			'action': 'do_login',
    		'url': 'http://www.hackforums.net/index.php',
    		'my_post_key': '60aae6001602ef2e0bd45033d53f53dd'
		}
		# first gather some resources to circumvent crawler protection - doesn't work
		# self.JSCrawl(self.Target)
		# self.JSCrawl(self.Target + 'forumdisplay.php?fid=232')
		return super(Crawler_Hackforums, self).Login(
			url, 
			self.Target + 'index.php', 
			post_data
		)

	# Overrides Crawler's crawl function
	def Crawl(self, max_date):
		# crawl of hackforums.net is executed in three steps:
		# 1. we retrieve all interesting forum posts
		# 2. we extract potential Booter URLs from these posts
		# 3. collect all related evidence and calculate scores 
		#    for later evaluation
		target_url = self.Target + 'forumdisplay.php?fid=232&page='
		### step 1. retrieve all relevant forum posts
		forum_items  	 = []
		current_page 	 = 1
		max_pages 	 	 = 1
		max_date_reached = False
		self.PrintUpdate('initiating crawling procedures: HackForums')
		self.PrintDivider()

		# crawl first forum page and parse into XML tree
		response = self.Session.post(target_url + str(current_page), headers=self.Header)
		tree 	 = html.fromstring(response.text) 

		# analyze structure and get relevant properties (via XPATH)
		self.PrintUpdate('analyzing structure and retrieving Booter candidates')
		self.PrintDivider()
		max_pages = int(tree.xpath('//a[@class="pagination_last"]/text()')[0])
		# max_pages = 1 # for debug
		# now start crawling
		while current_page <= max_pages and not max_date_reached:
			self.PrintUpdate('crawling page ' + str(current_page) + '/' + str(max_pages))
			self.PrintDivider()
            # get forum items
			forum_titles = tree.xpath('//td[contains(@class,"forumdisplay_")]/div/span[1]//a[contains(@class, " subject_")]/text()')
			forum_urls   = tree.xpath('//td[contains(@class,"forumdisplay_")]/div/span[1]//a[contains(@class, " subject_")]/@href')
			forum_dates  = tree.xpath('//td[contains(@class,"forumdisplay_")]/span/text()[1]')
        	# get data of each forum item
			for i in range(len(forum_titles)):
			    item = ForumItem(forum_titles[i], self.Target + forum_urls[i], forum_dates[i])
			    if item.IsPotentialBooter():
			        forum_items.append(item)
			        print(item)
			    # check if max date is reached
			    if item.Date < max_date:
			        max_date_reached = True
			        self.PrintDivider()
			        self.PrintUpdate('date limit reached; aborting...')
			        self.PrintDivider()
			        break
            # print a divider after each forum page
			self.PrintDivider()
            # get url of next page and re-iterate
			current_page = current_page + 1
			next_url     = target_url + str(current_page)
			response     = self.Session.post(next_url, headers=self.Header)
			tree         = html.fromstring(response.text)            
            
			if current_page <= max_pages:
			    self.Sleep()
    	# forum crawling is complete, print (sub)results
		self.PrintUpdate('items found: ' + str(len(forum_items)))
		self.PrintDivider()

    	### step 2. extract potential Booters from target forum posts
		self.PrintUpdate('attempting to obtain Booter URLs')
		self.PrintDivider()
		# start crawilng for each forum item
		counter = 0
		for item in forum_items:
			# parse html
			response = self.Session.post(item.URL, headers=self.Header)
			tree 	 = html.fromstring(response.text)
			url 	 = ''
			# check for URLs inside image tags
			tree_image = tree.xpath('(//tbody)[1]//div[contains(@class,"post_body")]//a[.//img and not(contains(@href, "hackforums.net")) and not(contains(@href, ".jpg") or contains(@href, ".png") or contains(@href, ".jpeg") or contains(@href, "gif"))]/@href')
			if tree_image:
			    url = tree_image[0]
			else:
				# otherwise check for URL in the post's content
				tree_links = tree.xpath('(//tbody)[1]//div[contains(@class,"post_body")]//a[not(@onclick) and not(contains(@href, "hackforums.net")) and not(contains(@href, ".jpg") or contains(@href, ".png") or contains(@href, ".jpeg") or contains(@href, ".gif"))]/@href')
				if tree_links:
				    url = tree_links[0]

			# add found url to list
			if url != '':
				self.AddToList(BooterURL(url), item.URL)

			# if a URL was found, resolve it and if succesful: add to list
			# if url != '' and not self.IsExcluded(BooterURL(url)):
			# 	try:
			# 		# response = self.Session.get(url, headers=self.Header)
			# 		status   = self.GetStatus(url) # returns tuple of resolved url, response code and status code

			# 		if status[1] == 200: # status[1] = response code
			# 			url = status[2] # status[2] = url
			# 		else:
			# 			# url was not properly resolved, determine cause
			# 			if status[1] == 503:
			# 				# blocked by cloudflare bot protection, use JS crawler
			# 				response = self.JSCrawl(status[2])
			# 				url = response.url if response.status_code == 200 else ''
			# 				status[1] = response.status_code
			# 				self.PrintLine('CRAWLER: bypassing cloudflare: ' + str(response.status_code) + ' | ' + response.url, Fore.MAGENTA)
			# 		# if URL was succesfully resolved (one way or another) add to list
			# 		if url != '' and status[1] == 200:
			# 			self.AddToList(BooterURL(url), item.URL, status[0])
			# 			self.PrintLine('CRAWLER: ' + url, Fore.BLUE)
			# 	except Exception as ex:
			# 		self.PrintError('EXCEPTION: ' + str(ex))
			# else:
			# 	# no potential booter detected (not found or excluded)
			# 	self.PrintLine('CRAWLER: no (potential) Booter detected', Fore.WHITE, Style.DIM)

			# print a divider line every 10 results (to keep things organized)
			counter = counter + 1
			if counter % 10 == 0:        
				self.PrintDivider()

		# finished, print results
		self.PrintDivider()
		self.PrintUpdate('DONE; Resolved: ' + str(len(self.URLs)) + ' Booter URLs')
		self.PrintDivider()
		
		### step 3. gather evidence and calculate scores per URL
		# for url in self.URLs:
