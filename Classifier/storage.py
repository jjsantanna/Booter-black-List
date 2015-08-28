# storage.py hosts several utility database functions for storage
import sqlite3

# open connection and retrieve (single) cursor
connection = sqlite3.connect('BOOTERS_TRAINING.db')

# saves a Booter Score in the database.
# if the website was not yet verified a row is inserted,
# otherwise updated.
def SaveScore(table, booterURL, last_update, typez, score):
	# check if booter's url already verified
	if RowExists(table, booterURL):
		Update(table, booterURL, 'lastUpdate', last_update) 
		Update(table, booterURL, typez, score) 
	else:
		# else, insert into database
		Insert(table, [booterURL, last_update, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
		Update(table, booterURL, typez, score) 


# saves a new weight distrubution in the database
def UpdateWeights(last_update, nr_pages, url_type, average_depth_level, average_url_length, domain_age, 
	domain_reservation_duration, whois_private, dps, page_rank, average_content_size, 
	outbound_hyperlinks, category_specific_dictionary, resolver_indication, terms_of_services_page,
	login_form_depth_level):
	table = 'weights'
	url_unqiue = 'ALL'
	# Update(table, url_unique, 'lastUpdate', last_update) 
	# Update(table, url_unique, 'nr_pages', nr_pages) 
	# Update(table, url_unique, 'url_type', url_type) 
	# Update(table, url_unique, 'average_depth_level', average_depth_level) 
	# Update(table, url_unique, 'average_url_length', average_url_length) 
	# Update(table, url_unique, 'domain_age', domain_age) 
	# Update(table, url_unique, 'domain_reservation_duration', domain_reservation_duration) 
	# Update(table, url_unique, 'whois_private', whois_private) 
	# Update(table, url_unique, 'dps', dps) 
	# Update(table, url_unique, 'page_rank', page_rank) 
	# Update(table, url_unique, 'average_content_size', average_content_size) 
	# Update(table, url_unique, 'outbound_hyperlinks', outbound_hyperlinks) 
	# Update(table, url_unique, 'category_specific_dictionary', category_specific_dictionary) 
	# Update(table, url_unique, 'resolver_indication', resolver_indication) 
	# Update(table, url_unique, 'terms_of_services_page', terms_of_services_page) 
	# Update(table, url_unique, 'login_form_depth_level', login_form_depth_level) 
	# more efficient version (only 1 db request/push)
	query  = 'UPDATE weights SET '
	query += 'lastUpdate = \'' + str(last_update) + '\', '
	query += 'nr_pages = ' + str(nr_pages) + ', '
	query += 'url_type = ' + str(url_type) + ', '
	query += 'average_depth_level = ' + str(average_depth_level) + ', '
	query += 'average_url_length = ' + str(average_url_length) + ', '
	query += 'domain_age = ' + str(domain_age) + ', '
	query += 'domain_reservation_duration = ' + str(domain_reservation_duration) + ', '
	query += 'whois_private = ' + str(whois_private) + ', '
	query += 'dps = ' + str(dps) + ', '
	query += 'page_rank = ' + str(page_rank) + ', '
	query += 'average_content_size = ' + str(average_content_size) + ', '
	query += 'outbound_hyperlinks = ' + str(outbound_hyperlinks) + ', '
	query += 'category_specific_dictionary = ' + str(category_specific_dictionary) + ', '
	query += 'resolver_indication = ' + str(resolver_indication) + ', '
	query += 'terms_of_services_page = ' + str(terms_of_services_page) + ', '
	query += 'login_form_depth_level = ' + str(login_form_depth_level)
	query += ' WHERE domainName = \'' + url_unique + '\''
	connection.execute(query)
	connection.commit()

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
	url = 'http://booter.xyz/register.php'
	SaveScore(url, '2015-06-26 11:08:30', '1.0')
