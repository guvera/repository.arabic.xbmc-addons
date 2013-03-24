import cookielib
import re
import urllib2
import os.path
from urllib2 import (urlopen, Request)
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup


TELEDUNET_URL = 'http://www.teledunet.com/'
TELEDUNET_TIMEPLAYER_URL = 'http://www.teledunet.com/tv/?file=rtmp://www.teledunet.com:1935/teledunet/%s'
HTML_FALLBACK = 'htmlfallback.html'

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

def _url(path=''):
	"""Returns a full url for the given path"""
	return urljoin(BASE_URL, path)

def get(url):
	"""Performs a GET request for the given url and returns the response"""
	try:	
		conn = urlopen(url)
		resp = conn.read()
		conn.close()
		return resp
	except IOError:
		pass
	return ""
	

def _html(url):
	"""Downloads the resource at the given url and parses via BeautifulSoup"""
	return BeautifulSoup(get(url), convertEntities=BeautifulSoup.HTML_ENTITIES)

def _get_channel_time_player(channel_name):
	url = TELEDUNET_TIMEPLAYER_URL % channel_name
	req = Request(url)
	req.add_header('Referer', TELEDUNET_URL)	# Simulate request is coming from website
	html = get(req)

	m = re.search('time_player=(.*);', html, re.M | re.I)
	time_player_str = eval(m.group(1))

	return repr(time_player_str).rstrip('0').rstrip('.')

def get_rtmp_params(channel_name):
	time_player_id = _get_channel_time_player(channel_name)

	return {
		'rtmp_url': 'rtmp://www.teledunet.com:1935/teledunet',
		'playpath': channel_name,
		'app': 'teledunet',
		'swf_url': ('http://www.teledunet.com/tv/player.swf?'
					'repeat=single&'
					'autostart=true&'
					'id0=%(time_player)s&'
					'streamer=rtmp://www.teledunet.com:1935/teledunet&'
					'file=%(channel_name)s&'
					'provider=rtmp'
					   ) % {'time_player': time_player_id, 'channel_name': channel_name},
		'video_page_url': TELEDUNET_TIMEPLAYER_URL % channel_name,
		'live': '1'
	}
	
def get_channels():

	html = _html(TELEDUNET_URL)
	color = '#009900'
	items = []

	for div in html.findAll("div", { "class":"div_channel" }):
		print div,
		onClickEl = div.findAll('a')[0]['onclick']
		m = re.search('.*\'(.*)\'.*', onClickEl, re.M|re.I)
		if m is not None:
			channel_name = m.group(1)
			# Remove the '+' at the End to get RTMP_Params 
			if channel_name.endswith('+'):
				channel_name = channel_name[:-1]
			print channel_name
			if color in div['style']:
				items.append({
					 'thumbnail': div.findAll('img')[0]['src'],
					 'label': '[COLOR green]%(channelname)s[/COLOR]' % {'channelname': div.find('font').contents[0]},
					 'path': channel_name
				})
			else :
				items.append({
				 'thumbnail': div.findAll('img')[0]['src'],
				 'label': div.find('font').contents[0],
				 'path': channel_name
				})
		
	if not items:
			path = os.path.join(os.path.dirname(__file__),HTML_FALLBACK)
			print path
			html = BeautifulSoup(''.join(open(path).readlines()), convertEntities=BeautifulSoup.HTML_ENTITIES)
			for div in html.findAll("div", { "class":"div_channel" }):
				print div,
				onClickEl = div.findAll('a')[0]['onclick']
				m = re.search('.*\'(.*)\'.*', onClickEl, re.M|re.I)
				if m is not None:
					channel_name = m.group(1)
					if channel_name.endswith('+'):
						channel_name = channel_name[:-1]
					print channel_name
					items.append({
						'thumbnail': div.findAll('img')[0]['src'],
						'label': div.find('font').contents[0],
						'path': channel_name
					})

	return items