RAPGENIUS_URL = 'http://rapgenius.com'
RAPGENIUS_SEARCH_URL = 'http://rapgenius.com/search'
RAPGENIUS_ARTIST_URL = 'http://rapgenius.com/artists'

from bs4 import BeautifulSoup
from urllib2 import urlopen
import re

#TODO - this
class artist:
	name = ""
	popularSongs = []
	songs = []


class song:
	name = ""
	link = ""
	artists = ""
	lyrics = ""


#Searches for 'artist', returns list of matches
#Currently list of strings - TODO - change to objects
def searchArtist(artist):
	searchUrl = RAPGENIUS_SEARCH_URL+'?q='+searchUrlFormat(artist)
	soup = BeautifulSoup(urlopen(searchUrl).read())
	results = []
	for row in soup.find_all('a', href=re.compile('/artists/.')):
		results.append(''.join(row.findAll(text=True)))
	return results

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
			songs.append((''.join(row.findAll(text=True)).strip(), RAPGENIUS_URL+row.get('href')))
	#TODO - object model

	print songs
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


def test():
	s = searchSong("Outkast Atliens")
	print getLyricsFromUrl(s[0][1])
test()
