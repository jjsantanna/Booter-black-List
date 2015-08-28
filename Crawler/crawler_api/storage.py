# storage.py hosts several utility database functions for storage
# of Booter and crawl-related results. 
from crawler_api.booter_url import BooterURL
# from booter_url import BooterURL # for when calling locally
import sqlite3
import datetime

# open connection and retrieve (single) cursor
# connection = sqlite3.connect('../BOOTERS.db') # for local call
# connection = sqlite3.connect('BOOTERS.db')
connection = sqlite3.connect('../RQ 3/BOOTERS_TRAINING.db')

# saves a Booter URL in the database.
# if the Booter URL was not yet found a row is inserted,
# otherwise updated.
def SaveURL(booterURL, source = '', status='?', notes=''):
	url = booterURL.URL
	url_unique = booterURL.UniqueName()
	# check if booter's url already exists
	if RowExists('urls', url_unique):
		# if entry exists, only do a necessary updates
		# Update('urls', url_unique, 'status', status) # disable again after manual verification of training set
		Update('urls', url_unique, 'timeUpdate', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) # so we can see which URLS are from august 1 onwards (test set)
		# also append source information if not yet stored
		sources = GetSingleValue('urls', url_unique, 'srcInformation')
		if source not in sources:
			Update('urls', url_unique, 'srcInformation', source if sources == '' else sources + ';' + source)
	else:
		# else, insert into database
		Insert('urls', [url_unique, url, 'CURRENT_DATE', '?', status, source, 'CURRENT_DATE', 'A', notes])

# saves a score vector of a single Booter in the database
# if the score vector was not yet found a row is inserted,
# otherwise updated.
def SaveScore(table, booterURL, 
	last_update, nr_pages, url_type, average_depth_level, average_url_length, domain_age, 
	domain_reservation_duration, whois_private, dps, page_rank, average_content_size, 
	outbound_hyperlinks, category_specific_dictionary, resolver_indication, terms_of_services_page,
	login_form_depth_level):
	url = booterURL.URL
	url_unique = booterURL.UniqueName()
	# check if booter's url already exists
	if RowExists(table, url_unique):
		# if entry exists, only do a necessary updates
		Update(table, url_unique, 'lastUpdate', last_update) 
		Update(table, url_unique, 'nr_pages', nr_pages) 
		Update(table, url_unique, 'url_type', url_type) 
		Update(table, url_unique, 'average_depth_level', average_depth_level) 
		Update(table, url_unique, 'average_url_length', average_url_length) 
		Update(table, url_unique, 'domain_age', domain_age) 
		Update(table, url_unique, 'domain_reservation_duration', domain_reservation_duration) 
		Update(table, url_unique, 'whois_private', whois_private) 
		Update(table, url_unique, 'dps', dps) 
		Update(table, url_unique, 'page_rank', page_rank) 
		Update(table, url_unique, 'average_content_size', average_content_size) 
		Update(table, url_unique, 'outbound_hyperlinks', outbound_hyperlinks) 
		Update(table, url_unique, 'category_specific_dictionary', category_specific_dictionary) 
		Update(table, url_unique, 'resolver_indication', resolver_indication) 
		Update(table, url_unique, 'terms_of_services_page', terms_of_services_page) 
		Update(table, url_unique, 'login_form_depth_level', login_form_depth_level) 
	else:
		# else, insert into database
		Insert(table, [url_unique, last_update, nr_pages, url_type, average_depth_level,
			average_url_length, domain_age, domain_reservation_duration, whois_private, dps,
			page_rank, average_content_size, outbound_hyperlinks, category_specific_dictionary,
			resolver_indication, terms_of_services_page, login_form_depth_level])	

# checks whether a row/entry already exists by comparing a 
# specific column with a check_value for uniqueness
def RowExists(table, url):
	query = 'SELECT domainName FROM ' + table + ' WHERE domainName = \'' + url + '\''
	cursor = connection.execute(query)
	if cursor.fetchall():
		return True
	else:
		return False

# returns a single value of a single column from the database
def GetSingleValue(table, key_value, column, key_column = 'domainName'):
	query = 'SELECT ' + column + ' FROM ' + table + ' WHERE ' + key_column + ' = \'' + key_value + '\''
	cursor = connection.execute(query)
	return cursor.fetchone()[0]

# utility function for easy insert statements
def Insert(table, values):
	query = 'INSERT INTO ' + table + ' VALUES ('
	for value in values:
		if value == 'CURRENT_DATE':
			query += value + ', '
		else:
			query += '\'' + str(value) + '\'' + ', '
	query = query[:-2] + ')'
	connection.execute(query)
	connection.commit()

# utility function for easy update statements
def Update(table, key, column, value):
	query = 'UPDATE ' + table + ' SET ' + column + ' = \'' + str(value) + '\' WHERE domainName = \'' + key + '\''
	connection.execute(query)
	connection.commit()

def Select(query):
	result = []
	for row in connection.execute(query):
		result.append(row)
	return result

def CloseConnection():
	connection.close()


# if explicitly called as root python file, do some debugging operations
if __name__ == "__main__":
	# store in database
	url = BooterURL('http://booter.xyz/register.php')
	SaveURL(url, 'joeydevries.com', 'Y')
	url = BooterURL('http://www.booter.io')
	SaveURL(url, 'learnopengl.com')