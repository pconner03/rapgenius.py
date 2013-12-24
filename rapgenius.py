#Big list of general changes I should make:
	#Organize code in a sane manner
		#I'm not a "real" python programmer, and I don't know the best organizations practices,
		#so everything is a mess right now

	#Exception handling
		#I let beautifulsoup/urllib throw everything for me.
		#Depending on what I decide proper use of this library should be, I can add
		#more specific exceptions, handling of network issues (timeout, 404, etc), and
		#handling of other errors I end up encountering

	#URL encoding
		#I'm really just guessing right now in things like searchUrlFormat()
		#That's bad. I shouldn't do that

	#Unicode?
		#Again, I'm not a "real" python developer, so I'm not sure how
		#it's magically handling unicode, or what the best practices for
		#stuff like that are

	#Really big requests
		#Fetching "all songs" for artists with a decent-sized catalog of songs
		#goes through all "pages" of the artist's songs, which is time consuming.
		#A nicer approach would be to allow users to specify an optional number
		#for either the number of 'pages' or number of songs to fetch in the request

		#Similarly, song (and maybe artist) search results paginate, but I haven't
		#tried handling this yet, so searches only give the first "page" of results.
		#Eventually, it should behave the same as the request for all artist songs,
		#with an optional size parameter

	#Documentation
		#Should be created, and it should be up-to-date if major changes are made to the code

	#Asynchronous data fetching
		#Eventually (i.e. after everything else has been worked out),
		#I could look into asynchronous/multithreaded data fetching.


RAPGENIUS_URL = 'http://rapgenius.com'
RAPGENIUS_SEARCH_URL = 'http://rapgenius.com/search'
RAPGENIUS_ARTIST_URL = 'http://rapgenius.com/artists'

from bs4 import BeautifulSoup
import urllib2
import re

#TODO - this
class artist:

	def __init__(self, name, url):
		self.name = name
		self.url = url

		self.popularSongs = [] #array of 'popular songs' from artist's page. Initially empty.
		self.songs = [] #array of songs on artist page that are not listed as 'popular songs.' Initially empty.
	
	def __str__(self):
		return self.name + ' - ' + self.url

	#instantiates object's popular song array and returns it
	def getPopularSongs(self):
		self.popularSongs = getArtistPopularSongs(self.url)
		return self.popularSongs


	#this pretty slow right now
	def getAllSongs(self):
		self.songs = getArtistSongs(self.url)



class song:

	def __init__(self, name, url):
		self.name = name
		self.url = url
		self.rawLyrics = ""
		#TODO - lyric + annotation stuff

	def __str__(self):
		return self.name + ' - ' + self.url

	def getRawLyrics(self):
		self.rawLyrics = getLyricsFromUrl(self.url)
		return self.rawLyrics

#Searches for 'artistName', returns list of matches
#returns list of artist objects
def searchArtist(artistName):
	searchUrl = RAPGENIUS_SEARCH_URL+'?q='+searchUrlFormat(artistName)
	soup = BeautifulSoup(urllib2.urlopen(searchUrl).read())
	results = []
	artistRe = re.compile('/artists/.')

	#if exact artist name is entered, rapgenius redirects to artist page
	if re.match('/artists/[0-9]*/follows', soup.find('a', href=artistRe).get('href')):
		#TODO - get actual artist name from artist url (to ensure proper capitalization, etc)
		results.append(artist(artistName, getArtistUrl(artistName)))

	for row in soup.find_all('a', href=artistRe):
		#print ''.join(row.findAll(text=True)) + RAPGENIUS_URL+row.get('href')
		results.append(artist(''.join(row.findAll(text=True)), RAPGENIUS_URL+row.get('href')))
	return results

def getArtistUrl(artistName):
	return RAPGENIUS_ARTIST_URL+"/" + artistName.replace(" ","-")#TODO - figure out other character replacements

#converts search query into something that can be put into search URL 
def searchUrlFormat(query):
	return query.replace(' ','+')#TODO check other cases

#returns array song objects
#TODO - same problem I had with getting all artist songs. With the urlopen request,
#		the results are paginated, and this currently only returns the first page
#		of results. Fix this + add depth/number of results feature eventually
def searchSong(songName):
	searchUrl = RAPGENIUS_SEARCH_URL+'?q='+searchUrlFormat(songName)
	soup = BeautifulSoup(urllib2.urlopen(searchUrl).read())
	songs = []
	for row in soup.find_all('a', class_='song_link'): #force to ignore 'hot song' results
		if(row.parent.get('class')!=None):
			songs.append(song(''.join(row.findAll(text=True)).strip(), RAPGENIUS_URL+row.get('href')))
	#TODO - object model

	#print songs
	return songs

#returns string of (unannotated) lyrics, given a url
def getLyricsFromUrl(url):
	#TODO - exeptions
	soup = BeautifulSoup(urllib2.urlopen(url).read())
	ret = ""
	for row in soup('div', {'class':'lyrics'}):
		text = ''.join(row.findAll(text=True))
		data = text.strip() +'\n'
		ret += data
	return data


def getArtistPopularSongs(url):
	soup = BeautifulSoup(urllib2.urlopen(url).read())
	songs = []
	for row in soup.find('ul', class_='song_list'):
		if(type(row.find('span'))!=int):
			songs.append(song(''.join(row.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+row.find('a').get('href')))
			
	return songs

def getArtistSongs(url):
	soup = BeautifulSoup(urllib2.urlopen(url).read())
	songs = []
	for row in soup.find('ul', class_='song_list').findNextSibling('ul'):
		try:
			songs.append( song(''.join(row.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+row.find('a').get('href') ))
		except:
			#Do nothing, cheap hack
			#TODO - see if there is a better way to do this
			pass
	#we currently have the first 'page' of song results
	#Now, we have to load the rest and add it to the list
	#Possible future feature: choosing depth (number of pages) or number of songs to load, rather than forcing everything
	#No proper error-checking yet, so this probably breaks for some artists
	for r in soup('div', {'class':'pagination'}):
		for row in r.findAll('a'): #TODO - see if I can make this prettier
			#print row.get('href')
			#print url+row.get('href')
			nextPage = BeautifulSoup(urllib2.urlopen(RAPGENIUS_URL+row.get('href')).read())
			for pageRow in nextPage.find('ul', class_='song_list'):
				if(type(pageRow.find('span'))!=int):
					#print ''.join(pageRow.find('span').findAll(text=True)).strip()
					songs.append(song(''.join(pageRow.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+pageRow.find('a').get('href')))

	return songs

def test():
	outkast = searchArtist("Outkast")[0]
	#print outkast.name
	#print outkast.url
	#outkast.getPopularSongs()
	#for song in outkast.popularSongs:
	#	print song.getRawLyrics()
	outkast.getAllSongs()
	for song in outkast.songs:
		print song.__str__()

#test()