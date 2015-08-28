from crawler_api.crawler_hackforums import Crawler_Hackforums
from crawler_api.crawler_google import Crawler_Google
from crawler_api.crawler_google2 import Crawler_Google2
from crawler_api.crawler_youtube import Crawler_Youtube
from crawler_api.crawler_facebook import Crawler_Facebook
from crawler_api.booter_url import BooterURL
from urllib.parse import urlparse
import crawler_api.storage
import datetime
import json
import random

results_google 	   = []
results_hackforums = []
results_youtube	   = []

###############################################################################
## GOOGLE                                                                    ##
## ############################################################################
# crawler = Crawler_Google(0)
# crawler.Crawl() # works, but only up to 100 queries per day
# results_google = crawler.Finish('crawl_google.txt')

try:
	###############################################################################
	## GOOGLE V2                                                                 ##
	## ############################################################################
	crawler = Crawler_Google2(1)
	# crawler.Crawl(200) # up to ~500 results (more is not possible by Google)
	# results_google = crawler.Finish('crawl_google2.txt')

	# print()
	# print()
	# print()

	###############################################################################
	## YOUTUBE                                                                   ##
	## ############################################################################
	crawler = Crawler_Youtube(1)
	# crawler.Crawl(100) # up to ~500 results (similar limit to Google)
	# results_youtube = crawler.Finish('crawl_youtube.txt')

	# print()
	# print()
	# print()

	###############################################################################
	## HACKFORUMS                                                                ##
	###############################################################################
	crawler = Crawler_Hackforums(1) # sleep level of 1
	# if crawler.Login():	# from time to time it might give a 5 sec check browser period; if so, simply manually solve this by visiting hackforums.net
	# 	print('login succesfull')
	# 	crawler.Crawl(datetime.datetime(2015, 3, 1)) # crawl up to may 15th
	# 	results_hackforums = crawler.Finish('crawl_hackforums.txt')

	# print()
	# print()
	# print()

except Exception as ex:
	print('GLOBAL EXCEPTION: ' + str(ex))



###############################################################################
## MERGE CRAWL RESULTS                                                       ##
###############################################################################
# final_results = []

# def IsDuplicate(booterURL):
# 	for i in range(0, len(final_results)):
# 		if booterURL.UniqueName() == final_results[i].UniqueName():
# 			return True
# 	return False		

# def AddResults(sub_results):
# 	for booterURL in sub_results:
# 		# we make the assumption the uniqueness of a Booter url is based on its
# 		# hostname only; thus we only have TYPE 1 URLs (prove this!)
# 		if not IsDuplicate(booterURL):
# 			final_results.append(booterURL)
# 		else:
# 			print('duplicate:' + booterURL.Full_URL)

# AddResults(results_google)
# AddResults(results_youtube)
# AddResults(results_hackforums)



# crawler.PrintDivider();
# crawler.PrintUpdate('completed crawling procedures; saving output to \'crawler_output.txt\'')
# with open('crawler_output.txt', 'w') as f:
	# for booterURL in final_results:
		# f.write(booterURL.UniqueName() + '\n')
		# json.dump(vars(booterURL), f)
		# f.write('\n')





###############################################################################
## SCRAPE AND GENERATE SCORES                                                ##
###############################################################################
crawler.PrintDivider();
crawler.PrintUpdate('INITIATING SCRAPING PROCEDURES;')
crawler.PrintDivider();

# query all to-scrape URLs
# from_date    = datetime.datetime(2015, 8, 1).strftime('%Y-%m-%d %H:%M:%S') # test_scores
# from_date    = datetime.datetime(2015, 8, 19).strftime('%Y-%m-%d %H:%M:%S') #test_scores2
from_date    = datetime.datetime(2015, 8, 20, 13, 30).strftime('%Y-%m-%d %H:%M:%S') #test_scores3
delay_period = 7
for url in crawler_api.storage.Select('SELECT fullURL FROM urls WHERE status != \'off\' AND timeUpdate >= \'' + str(from_date) + '\''):
	delay = delay_period + random.randint(0,14) # add a slight randomness to delay_period as to divide workload
	delay = 1
	crawler.Scrape(BooterURL(url[0]), delay)

# delay_period = 4; # re-scrape websites after last-update is 7 days
# for booterURL in final_results:
	# delay = delay_period + random.randint(0,7) # add a slight randomness to delay_period as to divide workload
	# crawler.Scrape(booterURL, delay)


crawler.PrintDivider();
crawler.PrintUpdate('DONE;')
crawler.PrintDivider();


# TESTING SCRAPE ALGORITHM
# crawler.Scrape(BooterURL('http://joeydevries.com'))
# crawler.Scrape(BooterURL('k-stress.pw'))
# crawler.Scrape(BooterURL('http://impulse101.org/'))
# crawler.Scrape(BooterURL('http://www.davidairey.com/'))
# crawler.Scrape(BooterURL('booter.org'))
# crawler.Scrape(BooterURL('joeyfladderak.com/'))
# crawler.Scrape(BooterURL('layer7.pw'))
# crawler.Scrape(BooterURL('tweakers.net'))
# crawler.Scrape(BooterURL('ragebooter.com'))
# crawler.Scrape(BooterURL('nl.urbandictionary.com'))
# crawler.Scrape(BooterURL('http://www.afkortingen.nu/ddos'))