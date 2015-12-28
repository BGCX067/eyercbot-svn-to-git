'''Processess incomming datalines into IRC functions.'''
import eyercbot
import eyercbot.log as log

class IRC:
    '''This class processess incomming IRC strings from the irc server into internal events. We use a class as getattr is used to assist this process.'''
    # These are functions for further parsing of the incoming data stream
    # They will forward proper variables to functions that are to be overloaded (above)
    def irc_JOIN(self, server, prefix, params):
        """
        Called when a user joins a channel.
        """
        nick = prefix.split('!')[0]
        host = prefix.split('!')[1]
        channel = params[-1]
        eyercbot.send('onJoin', server, nick, host, channel)
    
    def irc_KICK(self, server, prefix, params):
        """Kicked?  Who?  Not me, I hope.
        """
        kicker = prefix.split('!')[0]
        channel = params[0]
        kicked = params[1]
        message = params[-1]
        eyercbot.send('onKick', server, kicked, channel, kicker, message)
        
            
    def irc_MODE(self, server, prefix, params):
        user = prefix
        channel = params[0]
        modes = params[1]
        args = params[2:]
        # Add + if not specified
        # And this function theved from twisted
        if modes[0] not in "+-":
            modes = "+" + modes
        if ((modes[0] == '+' and '-' not in modes[1:]) or
            (modes[0] == '-' and '+' not in modes[1:])):
            # all modes are added or removed
            set = (modes[0] == '+')
            modes = modes[1:].replace('-+'[set], '')
            #self.modeChanged(user, channel, set, modes, tuple(args))
            eyercbot.send('onModeChange', server, user, channel, set, modes, tuple(args))
        else:
            # some modes added and other removed
            modes2, args2 = ['', ''], [[], []]
            for c in modes:
                if c == '+':
                    i = 0
                elif c == '-':
                    i = 1
                else:
                    modes2[i] += c
                    # take an arg only if the mode accepts it (e.g. +o nick)
                    if args and self._modeAcceptsArg.get(c, (False, False))[i]:
                        args2[i].append(args.pop(0))
            #if args:
            #    log.msg('Too many args (%s) received for %s. If one or more '
            #        'modes are supposed to accept an arg and they are not in '
            #        '_modeAcceptsArg, add them.' % (' '.join(args), modes))
            eyercbot.send('onModeChange', server, user, channel, True, modes2[0], tuple(args2[0]))
            eyercbot.send('onModeChange', server, user, channel, False, modes2[1], tuple(args2[1]))
            #self.modeChanged(user, channel, True, modes2[0], tuple(args2[0]))
            #self.modeChanged(user, channel, False, modes2[1], tuple(args2[1]))
        
    def irc_NICK(self, server, prefix, params):
        eyercbot.send('onNick', server, prefix.split('!')[0], params[0])
    
    def irc_NOTICE(self, server, prefix, parameters):
        """
        Called when we get a notice
        """
        user = prefix
        target = parameters[0]
        message = parameters[-1]
    
    def irc_PART(self, server, prefix, params):
        user, host = prefix.split('!')
        channel = params[0]
        reason = ""
        if len(params) > 1:
            reason = params[1]
        eyercbot.send('onPart', server, user, host, channel, reason)

    def irc_PRIVMSG(self, server, prefix, parameters):
        """
        Called when we get a private message.
        We then pipe to three possible functions:
        funcname1:  called for all private message
        funcname2:  called for all messages in channels
        funcname3:  called for all messages directly sent from users
        """
        sender = prefix
        target = parameters[0]
        message = parameters[-1]
        
        # Return if we got a blank message
        if not message:
            return
        # The logic which manages public vs private messages will be done one more level up.
        eyercbot.send('onMsg', server, sender, target, message)
    
    def irc_QUIT(self, server, prefix, params):
        nick, host = prefix.split('!')
        reason = params[0]
        eyercbot.send('onQuit', server, nick, host, reason)
    
    def irc_TOPIC(self, server, prefix, params):
        """
        Called when the topic for a channel is initially reported or when it
        subsequently changes.
        """
        #print(prefix, params)
        user = prefix
        channel = params[0]
        new_topic = params[1]
        eyercbot.send('onTopic', server, user, channel, new_topic)
    
    #def irc_TOPIC_SETTER(self, server, prefix, params):
        """
        not in RPL
        Notifices when topic is set and when
        """
        #user = string.split(prefix, '!')[0]
        #host = prefix
        #print("TOPIC SETTER:", prefix, params)
        #self.hostname, 333, user, channel, author, date
    #    channel = params[1]
    #    user = params[2]
    #    time = params[2]
        #self.topicinfo(channel, user, time)
    
    #
    # Err
    #
    
    def irc_ERR_NICKNAMEINUSE(self, server, prefix, params):
        '''Nickname in use'''
        bad_nick = params[1]
        # Attempt new nick
        #self.connection.send('NICK '+ bad_nick + '_\r\n')
        nick(server, bad_nick + '_')
        
    #
    # RPLs
    #
    
    def irc_RPL_BOUNCE(self,server, prefix, params):
        # 005 is doubly assigned.  Piece of crap dirty trash protocol.
        #if params[-1] == "are available on this server":
        #    self.isupport(params[1:-1])
        #else:
        #    self.bounce(params[1])
        pass
    
    def irc_RPL_CREATED(self, server, prefix, params):
        '''When server was created'''
        #self.created(params[1])
        pass
    
    def irc_RPL_ENDOFMOTD(self,server, prefix, params):
        pass
        #self.receivedMOTD(self.motd)
    
    def irc_RPL_LUSERCHANNELS(self, server, prefix, params):
        '''Lists channels on server'''
        #try:
        #    self.luserChannels(int(params[1]))
        #except ValueError:
        #    pass
        pass
    
    def irc_RPL_LUSERCLIENT(self, server, prefix, params):
        '''Lists number of users on server.'''
        #self.luserClient(params[1])
        pass
    
    def irc_RPL_LUSERME(self, server, prefix, params):
        '''More server info'''
        #self.luserMe(params[1])
        pass
    
    def irc_RPL_LUSEROP(self, server,prefix, params):
        '''Ops on server'''
        #try:
        #    self.luserOp(int(params[1]))
        #except ValueError:
        #    pass
        pass
    
    def irc_RPL_LUSERUNKNOWN(self, server, prefix, params):
        number = int(params[1])
        #self.luserunknown(number)
    
    def irc_RPL_MOTDSTART(self,server, prefix, params):
        pass
        #if params[-1].startswith("- "):
        #    params[-1] = params[-1][2:]
        #self.motd = [params[-1]]

    def irc_RPL_MOTD(self,server, prefix, params):
        pass
        #if params[-1].startswith("- "):
        #    params[-1] = params[-1][2:]
        #self.motd.append(params[-1])
    
    def irc_RPL_NAMREPLY(self, server, prefix, params):
        channel = params[2]
        nicks = params[3].split()
        eyercbot.send('onNameReply', server, channel, nicks)
        
    def irc_RPL_ENDOFNAMES(self, server, prefix, params):
        """
        Signle from server that it is finished sending names.  
        Shouldn't be needed for our purposes I think
        """
    
    def irc_RPL_MYINFO(self, server, prefix, params):
        #info = params[1].split(None, 3)
        #while len(info) < 4:
        #    info.append(None)
        #self.myInfo(*info)
        pass
    
    def irc_ERR_NOMOTD(self, server, prefix, params):
        '''Server is unable to open its MOTD file'''
        server = prefix
        target = params[0]
        explaination = params[1]
        log.info("Server is unable to offer a MOTD")

    def irc_RPL_TOPIC(self, server, prefix, params):
        """
        Called when the topic for a channel is initially reported or when it
        subsequently changes.
        """
        user = prefix
        channel = params[1]
        new_topic = params[2]
        eyercbot.send('onTopic', server, user, channel, new_topic)
    
    def irc_RPL_WELCOME(self, server, prefix, arguments):
        """
        Welcome from server, we launch, call signedOn
        """
        nick = arguments[0]
        message = arguments[1]
        eyercbot.send('signed on', server, nick, message)
    
    def irc_RPL_YOURHOST(self, server, prefix, params):
        #self.yourHost(params[1])
        # We may use this at some point to track the host for advanced cool stuff. But not now.
        pass

irc = IRC()

def process_message(server, line):
    '''Process incomming string and assignes it an IRC() function for further processing'''
    if not line:
        # If a douche sends us an empty line, screw them lets try again!
        return
    # Break message into prefix, command code, and arguments
    prefix = ''
    command = ''
    trailing = []
    if line[0] == ':':
        prefix, line = line[1:].split(' ', 1)
    if line.find(' :') != -1:
        line, trailing = line.split(' :', 1)
        arguments = line.split()
        arguments.append(trailing)
    else:
        arguments = line.split()
    command = arguments.pop(0)
    
    if command in numeric_to_symbolic:
        command = numeric_to_symbolic[command]
    # irc_ is added to prevent malicious servers
    method = getattr(irc, "irc_{0}".format(command), None)
    if method:
        method(server, prefix, arguments)
    else:
        log.warning('Command not yet implimented: ' + command)
        log.warning("Prefix: " + prefix)
        log.warning("Arguments: " + str(arguments))

eyercbot.messenger.add('process message', process_message)

# These functions process messages into IRC strings and ships them out.
def join(server, channel):
    """
    Join the specified channel
    """
    # If # and & is missing, add it
    if channel[0] != "#" and channel[0] != '&': 
        channel = "#" + channel
    eyercbot.send('send', server, 'JOIN {0}'.format(channel))
eyercbot.messenger.add('join channel', join)

def msg(server, target, text):
    """
    PRIVMSG text to user or channel
    """
    eyercbot.send('send', server, 'PRIVMSG {0} :{1}'.format(target, text))
eyercbot.messenger.add('msg', msg)

def nick(server, nick):
    '''Sends nick to server'''
    eyercbot.send('send', server, 'NICK ' + nick)
            
class OldIRC:
    """
    Old class: Process IRC data. 
    """
    # These commands are to be overloaded when inherited
        
    def allmsg(self, user, target, message):
        """
        Called when there is a message from a user or channel
        """
        pass
        
    def noticed(self, user, channel, message):
        """
        Called when I have a notice from a user to me or a channel.

        By default, this is equivalent to privmsg, but if your
        client makes any automated replies, you must not!
        From the RFC::
            The difference between NOTICE and PRIVMSG is that
            automatic replies MUST NEVER be sent in response to a
            NOTICE message. [...] The object of this rule is to avoid
            loops between clients automatically sending something in
            response to something it received.
        """
        pass
        
    def statsdline(self, stats):
        """
        Some servers provide a string for server statistics.
        """
    
    def user_parted(self, user, channel, reason):
        '''Called when user parts a channel the bot is in.'''
        pass
        
    # These are to be called from the bot/client
    # They can be overloaded if additional functionality is needed
    def kicked(self, kicked, channel, kicker, message):
        '''When a user, or self, is kicked from the channel.'''
        pass
        
    def part(self, channel):
        """
        Leaves channel
        """
        self.irc.send(self.encode('PART {0}'.format(channel)))
        
    def yourHost(self, info):
        """
        Called with daemon information about the server, usually at logon.
        @param when: A string describing what software the server is running, probably.
        """
        pass
        
    def created(self, when):
        """
        Called with creation date information about the server, usually at logon.
        @param when: A string describing when the server was created, probably.
        """
        
    def myInfo(self, servername, version, umodes, cmodes):
        """
        Called with information about the server, usually at logon.
        @param servername: The hostname of this server.
        @param version: A description of what software this server runs.
        @param umodes: All the available user modes.
        @param cmodes: All the available channel modes.
        """
    
    def bounce(self, info):
        """
        Called with information about where the client should reconnect.
        @param info: A plaintext description of the address that should be
        connected to.
        """
        #print("Bounce: " + info)
        
    def isupport(self, options):
        """Called with various information about what the server supports.
        @param options: Descriptions of features or limits of the server, possibly
        in the form "NAME=VALUE".
        """
    
    def luserClient(self, info):
        """
        Called with information about the number of connections, usually at logon.
        @param info: A description of the number of clients and servers
        connected to the network, probably.
        """
        
    def luserOp(self, ops):
        """Called with the number of ops logged on to the server.
        @type ops: C{int}
        """
        
    def luserChannels(self, channels):
        """Called with the number of channels existant on the server.
        @type channels: C{int}
        """
        
    def luserMe(self, info):
        """Called with information about the server connected to.
        @type info: C{str}
        @param info: A plaintext string describing the number of users and servers
        connected to this server.
        """
        
    def receivedMOTD(self, motd):
        """I received a message-of-the-day banner from the server.

        motd is a list of strings, where each string was sent as a seperate
        message from the server. To display, you might want to use::

            '\\n'.join(motd)

        to get a nicely formatted string.
        """
        #print("MOTD: " + str(motd))
        
    def n_local(self, current, max):
        """
        Number of people, current and max, on the local server
        """
        
    def n_global(self, current, max):
        """
        Number of people, current and max, on the entire entwork
        """
        
    def modeChanged(self, user, channel, set, modes, args):
        """Called when users or channel's modes are changed.

        @type user: C{str}
        @param user: The user and hostmask which instigated this change.

        @type channel: C{str}
        @param channel: The channel where the modes are changed. If args is
        empty the channel for which the modes are changing. If the changes are
        at server level it could be equal to C{user}.

        @type set: C{bool} or C{int}
        @param set: True if the mode(s) is being added, False if it is being
        removed. If some modes are added and others removed at the same time
        this function will be called twice, the first time with all the added
        modes, the second with the removed ones. (To change this behaviour
        override the irc_MODE method)

        @type modes: C{str}
        @param modes: The mode or modes which are being changed.

        @type args: C{tuple}
        @param args: Any additional information required for the mode
        change.
        """

    def luserunknown(self, number):
        """
        Number of unknown connections
        """

    def topic_updated(self, user, channel, new_topic):
        """In channel, user changed the topic to new_topic.

        Also called when first joining a channel.
        """
        
    def topicinfo(self, channel, user, time):
        """
        Identifies when the topic was changed and by who)
        """
    
    def nickChange(self, oldNick, newNick):
        """
        Called when there is a nick change
        """
    
    def userQuit(self, nick, host, message):
        """
        A user has left the server, and the messages they leave behind
        """
    
    def irc_RPL_N_LOCAL(self, prefix, params):
        min = 0
        max = 0
        line = params[1].split(": ")
        max = line[2]
        min = line[1].split(" ")[0]
        self.n_local(min, max)
        
    def irc_RPL_N_GLOBAL(self, prefix, params):
        min = 0
        max = 0
        line = params[1].split(": ")
        max = line[2]
        min = line[1].split(" ")[0]
        self.n_global(min, max)
        
    def irc_ERR_NOCHANMODES(self, prefix, params):
        print("Impliment: ERR_NOCHANMODES", prefix, params)

    def irc_ERR_NOCHANMODES(self, prefix, params):
        print("Impliment: RPL_NOCHANMODES", prefix, params)
        
    def irc_RPL_STATSDLINE(self, prefix, params):
        line = params[1]
        self.statsdline(line)
    
    def irc_ERR_UNKNOWNCOMMAND(self, prefix, params):
        log.warning('Unknown command: ' + str(prefix) + ', ' + str(params))
    
    def irc_ERR_LINETOOLONG(self, prefix, params):
        '''Client sent a line too long'''
    def irc_328(self, prefix, params):
        """
        328 does not seem to be in the RFCs
        """
        print("Unknown 328:", prefix, params)
        
# Constants (from RFC 2812)
# Shamleslly stolen from TWISTED
RPL_WELCOME = '001'
RPL_YOURHOST = '002'
RPL_CREATED = '003'
RPL_MYINFO = '004'
RPL_BOUNCE = '005'
RPL_USERHOST = '302'
RPL_ISON = '303'
RPL_AWAY = '301'
RPL_UNAWAY = '305'
RPL_NOWAWAY = '306'
RPL_WHOISUSER = '311'
RPL_WHOISSERVER = '312'
RPL_WHOISOPERATOR = '313'
RPL_WHOISIDLE = '317'
RPL_ENDOFWHOIS = '318'
RPL_WHOISCHANNELS = '319'
RPL_WHOWASUSER = '314'
RPL_ENDOFWHOWAS = '369'
RPL_LISTSTART = '321'
RPL_LIST = '322'
RPL_LISTEND = '323'
RPL_UNIQOPIS = '325'
RPL_CHANNELMODEIS = '324'
RPL_NOTOPIC = '331'
RPL_TOPIC = '332'
RPL_INVITING = '341'
RPL_SUMMONING = '342'
RPL_INVITELIST = '346'
RPL_ENDOFINVITELIST = '347'
RPL_EXCEPTLIST = '348'
RPL_ENDOFEXCEPTLIST = '349'
RPL_VERSION = '351'
RPL_WHOREPLY = '352'
RPL_ENDOFWHO = '315'
RPL_NAMREPLY = '353'
RPL_ENDOFNAMES = '366'
RPL_LINKS = '364'
RPL_ENDOFLINKS = '365'
RPL_BANLIST = '367'
RPL_ENDOFBANLIST = '368'
RPL_INFO = '371'
RPL_ENDOFINFO = '374'
RPL_MOTDSTART = '375'
RPL_MOTD = '372'
RPL_ENDOFMOTD = '376'
RPL_YOUREOPER = '381'
RPL_REHASHING = '382'
RPL_YOURESERVICE = '383'
RPL_TIME = '391'
RPL_USERSSTART = '392'
RPL_USERS = '393'
RPL_ENDOFUSERS = '394'
RPL_NOUSERS = '395'
RPL_TRACELINK = '200'
RPL_TRACECONNECTING = '201'
RPL_TRACEHANDSHAKE = '202'
RPL_TRACEUNKNOWN = '203'
RPL_TRACEOPERATOR = '204'
RPL_TRACEUSER = '205'
RPL_TRACESERVER = '206'
RPL_TRACESERVICE = '207'
RPL_TRACENEWTYPE = '208'
RPL_TRACECLASS = '209'
RPL_TRACERECONNECT = '210'
RPL_TRACELOG = '261'
RPL_TRACEEND = '262'
RPL_STATSLINKINFO = '211'
RPL_STATSCOMMANDS = '212'
RPL_ENDOFSTATS = '219'
RPL_STATSUPTIME = '242'
RPL_STATSOLINE = '243'
RPL_UMODEIS = '221'
RPL_SERVLIST = '234'
RPL_SERVLISTEND = '235'
RPL_STATSDLINE = '250'
RPL_LUSERCLIENT = '251'
RPL_LUSEROP = '252'
RPL_LUSERUNKNOWN = '253'
RPL_LUSERCHANNELS = '254'
RPL_LUSERME = '255'
RPL_ADMINME = '256'
RPL_ADMINLOC = '257'
RPL_ADMINLOC = '258'
RPL_ADMINEMAIL = '259'
RPL_TRYAGAIN = '263'
RPL_N_LOCAL = '265'
RPL_N_GLOBAL = '266'
ERR_NOSUCHNICK = '401'
ERR_NOSUCHSERVER = '402'
ERR_NOSUCHCHANNEL = '403'
ERR_CANNOTSENDTOCHAN = '404'
ERR_TOOMANYCHANNELS = '405'
ERR_WASNOSUCHNICK = '406'
ERR_TOOMANYTARGETS = '407'
ERR_NOSUCHSERVICE = '408'
ERR_NOORIGIN = '409'
ERR_NORECIPIENT = '411'
ERR_NOTEXTTOSEND = '412'
ERR_NOTOPLEVEL = '413'
ERR_WILDTOPLEVEL = '414'
ERR_BADMASK = '415'
ERR_UNKNOWNCOMMAND = '421'
ERR_NOMOTD = '422'
ERR_NOADMININFO = '423'
ERR_FILEERROR = '424'
ERR_NONICKNAMEGIVEN = '431'
ERR_ERRONEUSNICKNAME = '432'
ERR_NICKNAMEINUSE = '433'
ERR_NICKCOLLISION = '436'
ERR_UNAVAILRESOURCE = '437'
ERR_USERNOTINCHANNEL = '441'
ERR_NOTONCHANNEL = '442'
ERR_USERONCHANNEL = '443'
ERR_NOLOGIN = '444'
ERR_SUMMONDISABLED = '445'
ERR_USERSDISABLED = '446'
ERR_NOTREGISTERED = '451'
ERR_NEEDMOREPARAMS = '461'
ERR_ALREADYREGISTRED = '462'
ERR_NOPERMFORHOST = '463'
ERR_PASSWDMISMATCH = '464'
ERR_YOUREBANNEDCREEP = '465'
ERR_YOUWILLBEBANNED = '466'
ERR_KEYSET = '467'
ERR_CHANNELISFULL = '471'
ERR_UNKNOWNMODE = '472'
ERR_INVITEONLYCHAN = '473'
ERR_BANNEDFROMCHAN = '474'
ERR_BADCHANNELKEY = '475'
ERR_BADCHANMASK = '476'
ERR_NOCHANMODES = '477'
ERR_BANLISTFULL = '478'
ERR_NOPRIVILEGES = '481'
ERR_CHANOPRIVSNEEDED = '482'
ERR_CANTKILLSERVER = '483'
ERR_RESTRICTED = '484'
ERR_UNIQOPPRIVSNEEDED = '485'
ERR_NOOPERHOST = '491'
ERR_NOSERVICEHOST = '492'
ERR_UMODEUNKNOWNFLAG = '501'
ERR_USERSDONTMATCH = '502'

# And hey, as long as the strings are already intern'd...
symbolic_to_numeric = {
    "RPL_WELCOME": '001',
    "RPL_YOURHOST": '002',
    "RPL_CREATED": '003',
    "RPL_MYINFO": '004',
    "RPL_BOUNCE": '005',
    "RPL_LUSERUNKNOWN": "253",
    "RPL_N_LOCAL" : "265",
    "RPL_N_GLOBAL": "266",
    "RPL_USERHOST": '302',
    "RPL_ISON": '303',
    "RPL_AWAY": '301',
    "RPL_UNAWAY": '305',
    "RPL_NOWAWAY": '306',
    "RPL_WHOISUSER": '311',
    "RPL_WHOISSERVER": '312',
    "RPL_WHOISOPERATOR": '313',
    "RPL_WHOISIDLE": '317',
    "RPL_ENDOFWHOIS": '318',
    "RPL_WHOISCHANNELS": '319',
    "RPL_WHOWASUSER": '314',
    "RPL_ENDOFWHOWAS": '369',
    "RPL_LISTSTART": '321',
    "RPL_LIST": '322',
    "RPL_LISTEND": '323',
    "RPL_UNIQOPIS": '325',
    "RPL_CHANNELMODEIS": '324',
    "RPL_NOTOPIC": '331',
    "RPL_TOPIC": '332',
    "TOPIC_SETTER": "333",
    "RPL_INVITING": '341',
    "RPL_SUMMONING": '342',
    "RPL_INVITELIST": '346',
    "RPL_ENDOFINVITELIST": '347',
    "RPL_EXCEPTLIST": '348',
    "RPL_ENDOFEXCEPTLIST": '349',
    "RPL_VERSION": '351',
    "RPL_WHOREPLY": '352',
    "RPL_ENDOFWHO": '315',
    "RPL_NAMREPLY": '353',
    "RPL_ENDOFNAMES": '366',
    "RPL_LINKS": '364',
    "RPL_ENDOFLINKS": '365',
    "RPL_BANLIST": '367',
    "RPL_ENDOFBANLIST": '368',
    "RPL_INFO": '371',
    "RPL_ENDOFINFO": '374',
    "RPL_MOTDSTART": '375',
    "RPL_MOTD": '372',
    "RPL_ENDOFMOTD": '376',
    "RPL_YOUREOPER": '381',
    "RPL_REHASHING": '382',
    "RPL_YOURESERVICE": '383',
    "RPL_TIME": '391',
    "RPL_USERSSTART": '392',
    "RPL_USERS": '393',
    "RPL_ENDOFUSERS": '394',
    "RPL_NOUSERS": '395',
    "RPL_TRACELINK": '200',
    "RPL_TRACECONNECTING": '201',
    "RPL_TRACEHANDSHAKE": '202',
    "RPL_TRACEUNKNOWN": '203',
    "RPL_TRACEOPERATOR": '204',
    "RPL_TRACEUSER": '205',
    "RPL_TRACESERVER": '206',
    "RPL_TRACESERVICE": '207',
    "RPL_TRACENEWTYPE": '208',
    "RPL_TRACECLASS": '209',
    "RPL_TRACERECONNECT": '210',
    "RPL_TRACELOG": '261',
    "RPL_TRACEEND": '262',
    "RPL_STATSLINKINFO": '211',
    "RPL_STATSCOMMANDS": '212',
    "RPL_ENDOFSTATS": '219',
    "RPL_STATSUPTIME": '242',
    "RPL_STATSOLINE": '243',
    "RPL_UMODEIS": '221',
    "RPL_SERVLIST": '234',
    "RPL_SERVLISTEND": '235',
    "RPL_STATSDLINE": '250',
    "RPL_LUSERCLIENT": '251',
    "RPL_LUSEROP": '252',
    "RPL_LUSERUNKNOWN": '253',
    "RPL_LUSERCHANNELS": '254',
    "RPL_LUSERME": '255',
    "RPL_ADMINME": '256',
    "RPL_ADMINLOC": '257',
    "RPL_ADMINLOC": '258',
    "RPL_ADMINEMAIL": '259',
    "RPL_TRYAGAIN": '263',
    "ERR_NOSUCHNICK": '401',
    "ERR_NOSUCHSERVER": '402',
    "ERR_NOSUCHCHANNEL": '403',
    "ERR_CANNOTSENDTOCHAN": '404',
    "ERR_TOOMANYCHANNELS": '405',
    "ERR_WASNOSUCHNICK": '406',
    "ERR_TOOMANYTARGETS": '407',
    "ERR_NOSUCHSERVICE": '408',
    "ERR_NOORIGIN": '409',
    "ERR_NORECIPIENT": '411',
    "ERR_NOTEXTTOSEND": '412',
    "ERR_NOTOPLEVEL": '413',
    "ERR_WILDTOPLEVEL": '414',
    "ERR_BADMASK": '415',
    'ERR_LINETOOLONG': '417',
    "ERR_UNKNOWNCOMMAND": '421',
    "ERR_NOMOTD": '422',
    "ERR_NOADMININFO": '423',
    "ERR_FILEERROR": '424',
    "ERR_NONICKNAMEGIVEN": '431',
    "ERR_ERRONEUSNICKNAME": '432',
    "ERR_NICKNAMEINUSE": '433',
    "ERR_NICKCOLLISION": '436',
    "ERR_UNAVAILRESOURCE": '437',
    "ERR_USERNOTINCHANNEL": '441',
    "ERR_NOTONCHANNEL": '442',
    "ERR_USERONCHANNEL": '443',
    "ERR_NOLOGIN": '444',
    "ERR_SUMMONDISABLED": '445',
    "ERR_USERSDISABLED": '446',
    "ERR_NOTREGISTERED": '451',
    "ERR_NEEDMOREPARAMS": '461',
    "ERR_ALREADYREGISTRED": '462',
    "ERR_NOPERMFORHOST": '463',
    "ERR_PASSWDMISMATCH": '464',
    "ERR_YOUREBANNEDCREEP": '465',
    "ERR_YOUWILLBEBANNED": '466',
    "ERR_KEYSET": '467',
    "ERR_CHANNELISFULL": '471',
    "ERR_UNKNOWNMODE": '472',
    "ERR_INVITEONLYCHAN": '473',
    "ERR_BANNEDFROMCHAN": '474',
    "ERR_BADCHANNELKEY": '475',
    "ERR_BADCHANMASK": '476',
    "ERR_NOCHANMODES": '477',
    "ERR_BANLISTFULL": '478',
    "ERR_NOPRIVILEGES": '481',
    "ERR_CHANOPRIVSNEEDED": '482',
    "ERR_CANTKILLSERVER": '483',
    "ERR_RESTRICTED": '484',
    "ERR_UNIQOPPRIVSNEEDED": '485',
    "ERR_NOOPERHOST": '491',
    "ERR_NOSERVICEHOST": '492',
    "ERR_UMODEUNKNOWNFLAG": '501',
    "ERR_USERSDONTMATCH": '502',
}

numeric_to_symbolic = {}
for k, v in symbolic_to_numeric.items():
    numeric_to_symbolic[v] = k
