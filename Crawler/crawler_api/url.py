from urllib.parse import urlparse

# container format for potential Booter URL.
# Holds hostname/domain, complete URL and other 
# relevant data.
class BooterURL:
	# constructor
	def __init__(this, url):
		# if url does not contain protocol; add it.
		if 'http' not in url:
			url = 'http://' + url			
		# parse URL and store relevant data
		parsed 		  = urlparse(url)
		this.Hostname = parsed.hostname
		this.URL 	  = parsed.scheme + '://' + parsed.netloc + parsed.path;
		this.Full_URL = url

	# returns a URL representation that unique identifies the current URL 
	def UniqueName(this):
		# here we assume the hostname to be a unique identification 
		unique_name = this.Hostname.replace('www.','test.')
		print(unique_name)
		return unique_name

	def __str__(this):
		return this.UniqueName()

