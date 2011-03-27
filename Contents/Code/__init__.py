import urllib

PLUGIN_PREFIX = "/video/AskANinja"
ROOT = "http://www.askaninja.com/tag/recent"
BASE = "http://askaninja.com"
#CACHE_TIME = 86400

####################################################################################################

def Start():
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "Ask A Ninja", "icon-default.png", "art-default.png")
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	MediaContainer.title1 = L('Ask A Ninja')
	MediaContainer.viewGroup = 'List'
	MediaContainer.art = R('art-default.png')
#	HTTP.SetCacheTime(CACHE_TIME)
	
####################################################################################################
		
def MainMenu(sender=None, page=1):
	dir = MediaContainer()
	if page == 1:
		pageURL = ROOT
	else:
		pageURL = ROOT + '?page=' + str(page)
		dir.replaceParent = True
	for episode in HTML.ElementFromURL(pageURL).xpath('//div[@class="video"]'):
		link = episode.xpath('./div[@class="details"]/a')[0]
		title = link.text
		url = BASE + link.get('href')
		thumb = episode.xpath('./a/img')[0].get('src')
		dir.Append(Function(VideoItem(PlayEpisode, title=title, thumb=thumb), url=url))
	dir.Append(Function(DirectoryItem(MainMenu, title='More', thumb=R('icon-default.png')), page=page+1))
	return dir

def PlayEpisode(sender, url):
	redirectURL = HTML.ElementFromURL(url).xpath('//embed')[0].get('src')
	rssURL = urllib.unquote(urllib.urlopen(redirectURL).geturl().split('file=')[1])
	movieURL = XML.ElementFromURL(rssURL).xpath('//enclosure')[0].get('url')
	Log(movieURL)
	return Redirect(movieURL)