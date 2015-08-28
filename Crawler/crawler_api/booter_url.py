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
		this.Scheme   = parsed.scheme
		this.URL 	  = parsed.scheme + '://' + parsed.netloc + parsed.path
		this.Path     = parsed.path
		this.Query    = '?' + parsed.query if parsed.query != '' else ''
		this.Full_URL = url
		this.Status	  = '?'

	# returns a URL representation that unique identifies the current URL 
	def UniqueName(this):
		# here we assume the hostname to be a unique identification 
		protocol = this.Scheme + '://' if this.Scheme else ''
		if this.Hostname:			
			return this.Hostname.replace('www.','')
		else:
			return ''

	def __str__(this):
		return this.UniqueName()

