'''Search plugin.'''
# Search plugin to interface with different search services
import eyercbot
import re
import urllib.request
from urllib.parse import urlencode
import yaml
import eyercbot.log as log
import json
import xml.etree.ElementTree as etree
# Bold: 

# -------
# Config
# -------

# Defines the maximum length returned
# Later this will be expanded into two options, total maximum length and length per return

HAS_CONFIG = True
CONFIG_VERSION = 1
config = {"length": 400}
wiki_url = ""
wiki_search = ""
wiki_page = ""

google_search_url = 'http://ajax.googleapis.com/ajax/services/search/web'

default_headers = {
    'User-agent': 'Mozilla/5.0 (compatible; utils.web python module)'
    }

def wikipedia(server, user, target, message):
    '''Searches wikipedia for target phrase.'''
    wiki_url = 'http://en.wikipedia.org/w/api.php?format=yaml'
    wiki_search = '&action=query&list=search&srwhat=text&srlimit=1&srsearch='
    wiki_page = '&action=parse&prop=text&page='
    wiki = search_mediawiki(wiki_url, wiki_search, message)
    if not wiki:
        eyercbot.send('sendMsg', server, user, 'Found nothing with that search string.')
        return
    title, page, url = mediawiki(wiki_url, wiki_page, wiki)
    
    # Final html parsing and cleanup is done here
    # This should be abstracted out into a generic mediawiki function later
    if re.search('This <a .+>disambiguation</a>', page['parse']['text']['*']):
        result = 'This is a disambiguation page. Please be more specific.'
    
    html = page['parse']['text']['*']
    
    text = re.search('<p>(?P<text>.+)</p>', html).group('text')
    
    results = eyercbot.html2irc(text)
    # In some cases the results are way way too small
    # We try to see if we can pull a second paragraph
    if len(results) < 100:
        try:
            search2 =  re.search('<p>(?P<text1>.+?)</p>.*?<p>(?P<text2>.+?)</p>', html, flags=re.DOTALL)
            text = search2.group('text1') + ' ' + search2.group('text2')
            results = eyercbot.html2irc(text)
        except:
            pass
    
    # Trims results down to length
    if len(results) > eyercbot.config["plugin_config"]["search"]["length"]:
        results = results[0:eyercbot.config["plugin_config"]["search"]["length"]-3] + '...'
    results = re.sub(r'<[^<]*?/?>', "", results)
    url2 = 'http://en.wikipedia.org/wiki/' + urllib.request.quote(title)
    eyercbot.send('sendMsg', server, user, target, '' + title + ': ' + results)
    eyercbot.send('sendMsg', server, user, target, url2)

def wiktionary(server, user, target, message):
    '''Searches wikitionary for definition of that word.'''
    wiki_url = 'http://en.wiktionary.org/w/api.php?format=yaml'
    wiki_search = '&action=query&list=search&srwhat=text&srlimit=1&srsearch='
    wiki_page = '&action=parse&prop=text&page='
    wiki = search_mediawiki(wiki_url, wiki_search, message)
    if not wiki:
        eyercbot.send('sendMsg', server, user, 'Found nothing with that search string.')
        return
    title, page, url = mediawiki(wiki_url, wiki_page, wiki)
    
    # Final html parsing and cleanup is done here
    # This should be abstracted out into a generic mediawiki function later
    if re.search('This <a .+>disambiguation</a>', page['parse']['text']['*']):
        result = 'This is a disambiguation page. Please be more specific.'
    
    html = page['parse']['text']['*']
    
    text = re.search('<p>(?P<text>.+)</p>', html).group('text')
    
    results = eyercbot.html2irc(text)
    # In some cases the results are way way too small
    # We try to see if we can pull a second paragraph
    if len(results) < 100:
        try:
            search2 =  re.search('<p>(?P<text1>.+?)</p>.*?<p>(?P<text2>.+?)</p>', html, flags=re.DOTALL)
            text = search2.group('text1') + ' ' + search2.group('text2')
            results = eyercbot.html2irc(text)
        except:
            pass
    
    # Trims results down to length
    if len(results) > eyercbot.config["plugin_config"]["search"]["length"]:
        results = results[0:eyercbot.config["plugin_config"]["search"]["length"]-3] + '...'
    results = re.sub(r'<[^<]*?/?>', "", results)
    url2 = 'http://en.wiktionary.org/wiki/' + urllib.request.quote(title)
    eyercbot.send('sendMsg', server, user, target, '' + title + ': ' + results)
    eyercbot.send('sendMsg', server, user, target, url2)

def search_mediawiki(wiki_url, wiki_search, search_string):
    '''Uses mediawiki api to get page title of best match'''
    url = wiki_url + wiki_search + urllib.request.quote(search_string)
    wiki_yaml = urllib.request.urlopen(url).read().decode()#.replace('*', 'body', 1)
    page = yaml.load(wiki_yaml)
    if not page['query']['searchinfo']['totalhits']:
        return
    return page['query']['search'][0]['title']

def mediawiki(wiki_url, wiki_page, title):
    '''Looks up specific page'''
    url = wiki_url + wiki_page + urllib.request.quote(title)
    wiki_yaml = urllib.request.urlopen(url).read().decode()
    try:
        page = yaml.load(wiki_yaml)
    except:
        import json        
        wiki_json = urllib.request.urlopen(url.replace('yaml', 'json')).read().decode()
        page = json.loads(wiki_json)
    
    # Check for redirect
    if page['parse']['text']['*'].find('REDIRECT') != -1:
        title = re.search('<li>(REDIRECT:)|(REDIRECT) <a .+>(?P<title>.+)</a>', page['parse']['text']['*']).group('title')
        title, page, url = mediawiki(wiki_url, wiki_page, title)
    return title, page, url

def google(server, user, target, message):
    """Perform a search using Google's AJAX API.
    search("search phrase", options={})

    Valid options are:
        smallsearch - True/False (Default: False)
        filter - {active,moderate,off} (Default: "moderate")
        language - Restrict search to documents in the given language
                   (Default: "lang_en")
    """
    query = message
    headers = default_headers
    opts = {'q': query, 'v': '1.0'}
    url = urllib.request.Request(google_search_url + "?" + urlencode(opts), headers=headers)
    page = urllib.request.urlopen(url)
    results = json.loads(page.read().decode())
    page.close()
    url = results['responseData']['cursor']['moreResultsUrl']
    if not results['responseData']['results']:
        eyercbot.send('sendMsg', server, user, target, 'I found no results for that query.')
        return
    response = '' + results['responseData']['results'][0]['titleNoFormatting'] + ': ' + results['responseData']['results'][0]['url'] + ' | ' + results['responseData']['results'][0]['content']
    eyercbot.send('sendMsg', server, user, target, eyercbot.html2irc(response)[0:eyercbot.config["plugin_config"]["search"]["length"]])
    eyercbot.send('sendMsg', server, user, target, url)

def civilopedia(server, user, target, message):
    '''Searches http://civilopedia5.com/ using Google's site: parameter'''
    google(server, user, target, 'site:civilopedia5.com ' + message)

def weather(server, user, target, message):
    '''Prints out current weather conditions for tartget city. Parameters can include city, state; city, country; and US postal zip codes.'''
    if not message:
        eyercbot.send('sendMsg', server, user, target, weather.__doc__)
    url = 'http://www.google.com/ig/api?' + urlencode({'weather': message})
    weather_xml = urllib.request.urlopen(url).read().decode()
    root = etree.fromstring(weather_xml)
    weather_element = root[0]
    forcast_info = weather_element[0]
    current_conditions = weather_element[1]
    cityname = forcast_info.findall('city')[0].attrib['data']
    condition = current_conditions.findall('condition')[0].attrib['data']
    tempf = current_conditions.findall('temp_f')[0].attrib['data']
    tempc = current_conditions.findall('temp_c')[0].attrib['data']
    wind = current_conditions.findall('wind_condition')[0].attrib['data']
    response = 'Weather for ' + cityname + ': Temperature: ' + tempc + 'C (' + tempf + ' F). Condition: ' + condition + '. ' + wind
    eyercbot.send('sendMsg', server, user, target, response)
    
    
    

# The function maps the function to the input
# These need to be unique names, otherwise undesired plugin may be called!
alias_map = {"wiki": wikipedia, "google": google, "define": wiktionary, 'civilopedia5': civilopedia, 'weather': weather}
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
