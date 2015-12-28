'''Feed plugin. !search google searchterm will search google with searchterm and return the first result. @wikipedia searchterm will search wikipedia and return the first paragraph of the closest match. !search imdb movie title searches for movie title. !search noslang word will try to translate word.'''
import eyercbot
import eyercbot.httplib2 as httplib2
import urllib.request
from urllib.parse import urlencode

#import datetime
import re
import xml.etree.ElementTree as etree


# Bold: 

HAS_CONFIG = True
CONFIG_VERSION = 3
config = {'feeds':{'example name': {'url': 'http://nowhere.com/rss', 'servers': {'exampleServer': ['#example']},'lastid': '0'}},
    'frequency':'*/30 * * * *', 'length': 1000}

default_headers = {
    'User-agent': 'Mozilla/5.0 (compatible; utils.web python module)'
    }
    
# Normally cache should be used, however some feeds do not update their etag
# I'm looking at you civfanatics!
browser = httplib2.Http()

def auto_feed(*args):
    for feed in eyercbot.config['plugin_config']['feed']['feeds']:
        for server in eyercbot.config['plugin_config']['feed']['feeds'][feed]['servers']:
            for channel in eyercbot.config['plugin_config']['feed']['feeds'][feed]['servers'][server]:
                get_feed(server, '', channel, feed, auto=True)

def get_feed(server, user, target, message, auto=False):
    if not message:
        eyercbot.send('sendMsg', server, user, target, 'Please enter a feed name')
        return
    key = message
    if key not in eyercbot.config['plugin_config']['feed']['feeds']:
        eyercbot.send('sendMsg', server, user, target, 'Feed does not exist.')
        return
    response, content = browser.request(eyercbot.config['plugin_config']['feed']['feeds'][key]['url'])
    data = content.decode(response['content-type'].split('=')[1])
    tree = etree.fromstring(data)
    channel = tree.getchildren()[0]
    feedtitle = channel.find('title').text
    feedlink = channel.find('link').text
    child = channel.find('item')
    title = child.find('title').text
    link = child.find('link').text
    guid = child.find('guid').text
    if eyercbot.config['plugin_config']['feed']['feeds'][key]['lastid'] == guid and auto:
        return
    content = eyercbot.bbcode2irc(eyercbot.html2irc(child.find('{http://purl.org/rss/1.0/modules/content/}encoded').text))
    response = 'From: ' + feedtitle
    eyercbot.send('sendMsg', server, user, target, response)
    response = '' + title + ': ' + content
    #print("response:",response[0:400])
    eyercbot.send('sendMsg', server, user, target, response[:eyercbot.config['plugin_config']['feed']['length']])
    eyercbot.send('sendMsg', server, user, target, link)
    eyercbot.config['plugin_config']['feed']['feeds'][key]
    eyercbot.config['plugin_config']['feed']['feeds'][key]['lastid'] = guid

def list_feeds(server, user, target, message):
    eyercbot.send('sendMsg', server, user, target, str(list(eyercbot.config['plugin_config']['feed']['feeds'].keys())))
    

# The function maps the function to the input
# These need to be unique names, otherwise undesired plugin may be called!
alias_map = {"get feed": get_feed, 'list feeds': list_feeds}
        

if 'feed' in eyercbot.config['plugin_config']:
    minute, hour, day, month, day_of_week = eyercbot.config['plugin_config']['feed']['frequency'].split(' ')
    eyercbot.scheduler.add_cron_job(auto_feed, second='0', month=month, day=day, hour=hour, minute=minute, day_of_week=day_of_week)
#    eyercbot.scheduler.add("Feed auto update", 
#                datetime.datetime.utcnow() + datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds)), 
#                eyercbot.config['plugin_config']['feed']['frequency'], auto_feed)
    
'''      
shamelessly taken from the  rssnews.tcl for eggdrop

&quot;     \x22  &apos;     \x27  &amp;      \x26  &lt;       \x3C
        &gt;       \x3E        \x20  &iexcl;    \xA1  &curren;   \xA4
        &cent;     \xA2  &pound;    \xA3  &yen;      \xA5  &brvbar;   \xA6
        &sect;     \xA7  &uml;      \xA8  &copy;     \xA9  &ordf;     \xAA
        &laquo;    \xAB  &not;      \xAC  &shy;      \xAD  &reg;      \xAE
        &macr;     \xAF  &deg;      \xB0  &plusmn;   \xB1  &sup2;     \xB2
        &sup3;     \xB3  &acute;    \xB4  &micro;    \xB5  &para;     \xB6
        &middot;   \xB7  &cedil;    \xB8  &sup1;     \xB9  &ordm;     \xBA
        &raquo;    \xBB  &frac14;   \xBC  &frac12;   \xBD  &frac34;   \xBE
        &iquest;   \xBF  &times;    \xD7  &divide;   \xF7  &Agrave;   \xC0
        &Aacute;   \xC1  &Acirc;    \xC2  &Atilde;   \xC3  &Auml;     \xC4
        &Aring;    \xC5  &AElig;    \xC6  &Ccedil;   \xC7  &Egrave;   \xC8
        &Eacute;   \xC9  &Ecirc;    \xCA  &Euml;     \xCB  &Igrave;   \xCC
        &Iacute;   \xCD  &Icirc;    \xCE  &Iuml;     \xCF  &ETH;      \xD0
        &Ntilde;   \xD1  &Ograve;   \xD2  &Oacute;   \xD3  &Ocirc;    \xD4
        &Otilde;   \xD5  &Ouml;     \xD6  &Oslash;   \xD8  &Ugrave;   \xD9
        &Uacute;   \xDA  &Ucirc;    \xDB  &Uuml;     \xDC  &Yacute;   \xDD
        &THORN;    \xDE  &szlig;    \xDF  &agrave;   \xE0  &aacute;   \xE1
        &acirc;    \xE2  &atilde;   \xE3  &auml;     \xE4  &aring;    \xE5
        &aelig;    \xE6  &ccedil;   \xE7  &egrave;   \xE8  &eacute;   \xE9
        &ecirc;    \xEA  &euml;     \xEB  &igrave;   \xEC  &iacute;   \xED
        &icirc;    \xEE  &iuml;     \xEF  &eth;      \xF0  &ntilde;   \xF1
        &ograve;   \xF2  &oacute;   \xF3  &ocirc;    \xF4  &otilde;   \xF5
        &ouml;     \xF6  &oslash;   \xF8  &ugrave;   \xF9  &uacute;   \xFA
        &ucirc;    \xFB  &uuml;     \xFC  &yacute;   \xFD  &thorn;    \xFE
        &yuml;     \xFF
'''
