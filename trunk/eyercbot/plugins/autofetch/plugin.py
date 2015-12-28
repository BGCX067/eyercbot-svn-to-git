'''Plugin which automaticly fetches information from links and such'''
import eyercbot
import eyercbot.httplib2 as httplib2
import re

HAS_CONFIG = False

browser = httplib2.Http()

def publicmsg(server, nick, target, message):
    '''Reads the message, looking for specific things to autofetch and post.'''
    # Youtube title
    if 'http://www.youtube.com/watch' in message:
        re1='((?:http|https)(?::\\/{2}[\\w]+)(?:[\\/|\\.]?)(?:[^\\s"]*))'	# HTTP URL 1

        rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
        m = rg.search(message)
        if m:
            url=m.group(1)        
        response, content = browser.request(url)
        html = content.decode()
        query = re.search('<title>(?P<title>.+?)</title>',html,flags=re.DOTALL)
        title = query.group('title').replace('\n','')
        eyercbot.send('msg', server, target, title)

event_map = {'onPubmsg': publicmsg}