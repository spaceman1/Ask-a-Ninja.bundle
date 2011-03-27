import urllib
import re

PLUGIN_PREFIX = "/video/AskANinja"
ROOT = "http://www.askaninja.com/tag/recent"
BASE = "http://askaninja.com"

YOUTUBE_VIDEO_FORMATS = ['Standard', 'Medium', 'High', '720p', '1080p']
YOUTUBE_FMT = [34, 18, 35, 22, 37]
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
	youTubeCookies = HTTP.GetCookiesForURL('http://www.youtube.com/')
	dir.httpCookies = youTubeCookies
	
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
	page  = HTML.ElementFromURL(url)
	try:
		redirectURL = page.xpath('//embed')[0].get('src')
	except IndexError:
		link = 'http://www.youtube.com/watch?v=' + page.xpath('//iframe')[0].get('src').split('/')[-1].split('?')[0]
		Log(link)
		return PlayYouTubeVideo(None, link)
	rssURL = urllib.unquote(urllib.urlopen(redirectURL).geturl().split('file=')[1])
	movieURL = XML.ElementFromURL(rssURL).xpath('//enclosure')[0].get('url')
	Log(movieURL)
	return Redirect(movieURL)

def PlayYouTubeVideo(sender, url):
	yt_page = HTTP.Request(url, cacheTime=1).content
	#yt_page = HTTP.Request(YOUTUBE_VIDEO_PAGE % (video_id), cacheTime=1).content

	fmt_url_map = re.findall('"fmt_url_map".+?"([^"]+)', yt_page)[0]
	fmt_url_map = fmt_url_map.replace('\/', '/').split(',')

	fmts = []
	fmts_info = {}

	for f in fmt_url_map:
		(fmt, url) = f.split('|')
		fmts.append(fmt)
		fmts_info[str(fmt)] = url

	index = 0
	if YOUTUBE_FMT[index] in fmts:
		fmt = YOUTUBE_FMT[index]
	else:
		for i in reversed( range(0, index+1) ):
			if str(YOUTUBE_FMT[i]) in fmts:
				fmt = YOUTUBE_FMT[i]
				break
			else:
				fmt = 5

	url = fmts_info[str(fmt)]
	url = url.replace('\\u0026', '&')
	Log(url)
	return Redirect(url)
