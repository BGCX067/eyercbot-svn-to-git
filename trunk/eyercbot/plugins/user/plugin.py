"""
User plugin
2009 croxis
"""

from eyercbot.users import userdb
import eyercbot
import urllib.request
import eyercbot.log as log

HAS_CONFIG = False

def register(server, user, target, message):
    eyercbot.send('sendMsg', server, user, target, "Too lazy to impliment yet")

def whoami(server, user, target, message):
    '''Reports to user what the bot knows about them'''
    userO = userdb.getUser(user)
    eyercbot.send('sendMsg', server, user, target, "You are: " + userO.nick + " in group " + userO.group + '. Registration: ' + str(userO.registered) + '. Permissions: ' + str(userO.permissions))

def add_whitelist(server, user, target, message):
	'''@add whitelist group_name, whitelist.function | Adds whitelist to target group.'''
	if len(message.split(', ')) != 2:
		eyercbot.send('sendMsg', server, user, target, "Invalid syntax")
		return
	group_name, permission = message.split(', ')
	eyercbot.send('sendMsg', server, user, target, "Unfinished function")
	

def geolocate(server, user, target, message):
    log.debug("Geolocate: " + message)
    i = 0
    help = """
            Made by Daniel Folkes
    ==============================
            Usage:
                    python ipmap.py 74.125.45.100 all
            Args:
                    all =   Prints all details
                    nomap = Gets All, no map
                    loc =   Gets: Country, Region, City
    """
    # pull ip
    
    #print(user)
    ip = message
    
    comm = "loc"
    response = urllib.request.urlopen("http://www.ipmap.com/"+ip)
    pg = response.read().decode("utf8")
     
    pg = pg[pg.find('<table'):pg.find('<div id="footer"')]
     
     
    st = pg.find('<td>')
    st2 = pg.find('&nbsp;')
    ed = pg.find('</tr')
    info0 = pg[st+4:st2]
     
    pg = pg[ed+4:]
     
    st = pg.find('<td>')
    st2 = pg.find('&nbsp;')
    ed = pg.find('</tr')
    info1 = pg[st+4:st2]
     
     
    pg = pg[ed+4:]
     
    st = pg.find('<td>')
     
    st = pg.find('<td>')
    st2 = pg.find('&nbsp;')
    ed = pg.find('</tr')
    info2 = pg[st+4:st2]
     
    pg = pg[ed+4:]
     
    st = pg.find('<td>')
    st2 = pg.find('&nbsp;')
    ed = pg.find('</tr')
    info3 = pg[st+4:st2]
     
     
    pg = pg[ed+4:]
     
    st = pg.find('<td>')
    st2 = pg.find('&nbsp;')
    ed = pg.find('</tr')
    info4 = pg[st+4:st2]
     
    pg = pg[ed+4:]
     
    st = pg.find('<td>')
    st2 = pg.find('&nbsp;')
    ed = pg.find('</tr')
    info5 = pg[st+4:st2]
     
     
    pg = pg[ed+4:]
     
    st = pg.find('<td>')
    st2 = pg.find('&nbsp;')
    ed = pg.find('</tr')
    info6 = pg[st+4:st2]
     
    pg = pg[ed+4:]
     
    st = pg.find('<img src="http://maps.google.com')
    st2 = pg.find('"/>')
    #ed = pg.find('')
    info7 = pg[st:st2+3]
     
     
    retval = ""
    sep = ","
    if comm == "nomap":
            retval += info0
            retval += sep
            retval += info1
            retval += sep
            retval += info1
            retval += sep
            retval += info2
            retval += sep
            retval += info3
            retval += sep
            retval += info4
            retval += sep
            retval += info5
            retval += sep
            retval += info6
    elif comm == "loc":
            retval += info3
            retval += sep
            retval += info4
            retval += sep
            retval += info5
    else:
            retval += info0
            retval += sep
            retval += info1
            retval += sep
            retval += info2
            retval += sep
            retval += info3
            retval += sep
            retval += info4
            retval += sep
            retval += info5
            retval += sep
            retval += info6
            retval += sep
            retval += info7
     
    eyercbot.send('sendMsg', server, user, target, ip + ' is in ' + retval)

# The function maps the function to the input
# These need to be unique names, otherwise undesired plugin may be called!
alias_map = {"user register": register, "register user": register, "register": register, 'who am i': whoami,
    'where is': geolocate}