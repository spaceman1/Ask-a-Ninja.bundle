from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

import re

PLUGIN_PREFIX = "/video/AskANinja"
ROOT = "http://askaninja.com/episodes"
BASE = "http://askaninja.com"
CACHE_TIME = 86400

# Known dead links: 3499, 5564
# 3499: no quicktime
# 5564: no video
####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "Ask A Ninja", "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  MediaContainer.title1 = L('Ask A Ninja')
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R('art-default.png')
  HTTP.SetCacheTime(CACHE_TIME)
  
def UpdateCache():
  knownEpisodes = MediaContainer()  
  
  hasMorePages = True
  page = 0
  while hasMorePages:
    hasMorePages = False
    for episode in scrapeEpisodes(page):
      if 'title' in episode.__dict__:
        if 'Classic' not in episode.title:
          knownEpisodes.Append(episode)
      else:
        hasMorePages = True
        page = page + 1
  Dict.Set('episodes', knownEpisodes)
  urls = list()
  for episode in knownEpisodes:
    EpisodeMenu('', episode._Function__kwargs['url'])
  return
####################################################################################################
def MainMenu():
  return EpisodesMenu('', 0)

def EpisodesMenu(sender, page):
  knownEpisodes = Dict.Get('episodes')
  if knownEpisodes != None:
    return knownEpisodes
  else:
    return scrapeEpisodes(page)
    
def scrapeEpisodes(page):
  dir = MediaContainer()
  if page == 0:
    pageURL = ROOT
  else:
    pageURL = ROOT + '?page=' + str(page)
    dir.replaceParent = True
  for episode in GetFixedXML(pageURL, True).xpath('//div[@class="ninja_video"]'):
    try:
      title = episode.xpath('child::div/div/a')[0].get('title')
      url = episode.xpath('child::div/div/a')[0].get('href')
      thumb = episode.xpath('child::div/div/a/img')[0].get('src')
    except:
      try:
        title = episode.xpath('child::div/a')[0].text
        url = episode.xpath('child::div/a')[0].get('href')
        thumb = ''
      except:
        title = episode.xpath('child::a')[0].text
        url = episode.xpath('child::a')[0].get('href')
        thumb = ''
    url = BASE + url
    dir.Append(Function(VideoItem(EpisodeMenu, title=title, thumb=thumb), url=url))
  if len(GetFixedXML(pageURL, True).xpath('//a[starts-with(text(), "next")]')) != 0:
    dir.Append(Function(DirectoryItem(EpisodesMenu, title='More'), page=page + 1))
  return dir
  
  
def EpisodeMenu(sender, url):
  try:
    src = GetFixedXML(url, True).xpath('//a[text()="Quicktime/MP4"]')[0].get('href')
  except:
    src = ''
  if not src.endswith('.mp4') and not src.endswith('.mov') and not src.endswith('.m4v'):
    try:
      src = GetFixedXML(url, True).xpath('//a[text()="iPod"]')[0].get('href')
    except:
      pass
  if not src.endswith('.mp4') and not src.endswith('.mov') and not src.endswith('.m4v'):
    try:
      src = GetFixedXML(url, True).xpath('//a[text()="iPod/Quicktime"]')[0].get('href')
    except:
      pass
  if not src.endswith('.mp4') and not src.endswith('.mov') and not src.endswith('.m4v'):
    try:
      src = GetFixedXML(url, True).xpath('//a[text()="Quicktime/iPod"]')[0].get('href')
    except:
      pass
  if not src.endswith('.mp4') and not src.endswith('.mov') and not src.endswith('.m4v'):
    try:
      src = GetFixedXML(url, True).xpath('//a[contains(text(), "Click here to Download this movie.")]')[0].get('href')
    except:
      pass
  if not src.endswith('.mp4') and not src.endswith('.mov') and not src.endswith('.m4v'):
    try:
      src = BASE + GetFixedXML(url, True).xpath('//a[contains(text(), "quicktime")]')[0].get('href')
      src = GetFixedXML(src, True).xpath('//div[@class="content"]/object/param[@name="src"]')[0].get('value')
    except:
      Log('No video found for ' + url)
      return Redirect(noMedia)
  return Redirect(src)
  
def noMedia(sender):
  return MessageContainer('No video found', 'No high-res video was found. Try using a web browser to view this talk.')
####################################################################################################  
def GetXML(url, use_html_parser=False, encoding='utf8'):
  return XML.ElementFromURL(url, use_html_parser, encoding)

def GetFixedXML(url, use_html_parser=False, encoding='utf8'):
  return XML.ElementFromString(descape(HTTP.Request(url, encoding=encoding)), use_html_parser)

def descape_entity(m):
  entity = m.group(1)
  if entity == "raquo":
    return "_"
  if entity == "nbsp":
    return " "
  return m.group(0)
    
def descape(string):
  pattern = re.compile("&(\w+?);")
  pattern2 = re.compile(u'[\u201c\u201d]')
  return pattern2.sub('"', pattern.sub(descape_entity, string))
  