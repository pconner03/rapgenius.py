RAPGENIUS_URL = 'http://rapgenius.com'
RAPGENIUS_SEARCH_URL = 'http://rapgenius.com/search'
RAPGENIUS_ARTIST_URL = 'http://rapgenius.com/artists'

from bs4 import BeautifulSoup
from urllib2 import urlopen
import re

#TODO - this
class artist:

	def __init__(self, name, url):
		self.name = name
		self.url = url

		self.popularSongs = [] #array of 'popular songs' from artist's page. Initially empty.
		self.songs = [] #array of songs on artist page that are not listed as 'popular songs.' Initially empty.
	
	#instantiates object's popular song array and returns it
	def getPopularSongs(self):
		self.popularSongs = getArtistPopularSongs(self.url)
		return self.popularSongs

	def getAllSongs(self):
		self.songs = getArtistSongs(self.url)


class song:

	def __init__(self, name, url):
		self.name = name
		self.url = url
		self.rawLyrics = ""
		#TODO - lyric + annotation stuff
	def getRawLyrics(self):
		self.rawLyrics = getLyricsFromUrl(self.url)
		return self.rawLyrics

#Searches for 'artist', returns list of matches
#Currently list of strings - TODO - change to objects
def searchArtist(artistName):
	searchUrl = RAPGENIUS_SEARCH_URL+'?q='+searchUrlFormat(artistName)
	soup = BeautifulSoup(urlopen(searchUrl).read())
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

#returns array of tuples where index0 = song name, index1 = song url
def searchSong(song):
	searchUrl = RAPGENIUS_SEARCH_URL+'?q='+searchUrlFormat(song)
	soup = BeautifulSoup(urlopen(searchUrl).read())
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
	soup = BeautifulSoup(urlopen(url).read())
	ret = ""
	for row in soup('div', {'class':'lyrics'}):
		text = ''.join(row.findAll(text=True))
		data = text.strip() +'\n'
		ret += data
	return data


def getArtistPopularSongs(url):
	soup = BeautifulSoup(urlopen(url).read())
	songs = []
	for row in soup.find('ul', class_='song_list'):
		if(type(row.find('span'))!=int):
			songs.append(song(''.join(row.find('span').findAll(text=True)).strip(), RAPGENIUS_URL+row.find('a').get('href')))
			
	return songs

def getArtistSongs(url):
	#TODO - implement this
	#For now, just return popular songs
	return getArtistPopularSongs(url)

def test():
	outkast = searchArtist("Outkast")[0]
	#print outkast.name
	#print outkast.url
	outkast.getPopularSongs()
	for song in outkast.popularSongs:
		print song.getRawLyrics()


