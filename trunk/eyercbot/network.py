'''
Handles IRC network stuff
Lot of code inspired or lifted from twisted or irclib
'''

import socket, threading, queue, time
import eyercbot.log as log
import eyercbot

# connections = {'server name': Connection()}
connections = {}

class IRCConnection(threading.Thread):
    '''Basic IRC connection.'''
    def __init__(self, name, server, port):
        '''Socket lock is when the socket is being used only. Other lock for everything else'''
        threading.Thread.__init__(self)
        #self.daemon = True
        self.sock = None
        self.name = name
        self.server = server
        self.port = port
        self.running = False
        self.incomplete_buffer = ''
        self.lock = threading.Lock()
        self.socket_lock = threading.Lock()
        self.i = 0
    
    def send(self, line, encode="utf-8"):
        """
        Preps string to binary and sends to server. These replacements are a last fix in case any undesired carrage returns make it through.
        """
        self.socket_lock.acquire()
        line = line.replace('\r', '')
        line = line.replace('\n', ' ')
        line = line.replace('\r\n', '') + '\r\n'
        self.sock.send(line.encode(encode))
        self.socket_lock.release()
    
    def connect(self, nick, username, hostname, servername, realname, timeout=0.2):
        self.socket_lock.acquire()
        log.info('Connecting to ' + self.name)
        self.sock = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.sock.connect(( self.server, self.port))
        self.nick = nick
        nick_line = 'NICK '+ self.nick + '\r\n'
        self.sock.send ( nick_line.encode('utf-8') )
        self.username = username
        self.hostname = hostname
        self.servername = servername
        self.realname = realname
        user_line = 'USER {0} {1} {2} :{3}\r\n'.format(username, hostname, servername, realname)
        self.sock.send(user_line.encode('utf-8'))
        self.sock.settimeout(timeout)
        self.socket_lock.release()
    
    def run(self):
        """
        Calls run once
        """
        #self.sock.setblocking(False)
        self.running = True
        while self.running:
            self.run_once()
            # Prevent cpu oversaturation
            time.sleep(0.1)
        self.sock.close()
        
    def run_once(self):
        """
        Process the buffer and queue once.  Will need to be checked every now and then.
        run_forever is more useful
        """
        #self.lock.acquire()
        data = None
        try:
            #self.socket_lock.acquire()
            d = self.sock.recv(4096)
            data = d.decode('utf_8', 'replace')
            #self.socket_lock.release()
        except socket.timeout:
            #print("Timeout:", self.i)
            #self.i += 1
            pass
        except:
            # Just incase except code fails
            #import traceback
            #traceback.print_exc(file=open("errlog.txt","a"))
            log.exception("Critical Error:")
            #self.running = False
            #eyercbot.send('add connection', self.name, self.server, self.port)
            #eyercbot.send('connect', self.name, self.nick, self.username, self.hostname, self.servername, self.realname, timeout=0.2)
            #eyercbot.send('start server', self.name)  
            self.connect(self.name, self.nick, self.username, self.hostname, self.servername, self.realname, timeout=0.2)
        #self.lock.release()
        if data:
            self.process_data(data)
        
    def process_data(self, data):
        """
        For internal use only
        Processes incomming data
        """
        self.lock.acquire()
        # An incomplete buffer is present: add to data and clear
        if self.incomplete_buffer:
            data = self.incomplete_buffer + data
            self.incomplete_buffer = ""
        # Test to see if we have an incomplete line at end
        # If so we will add it to the incomplete buffer
        # as we process the data
        if data[-2:] == "\r\n":
            split_data = data.split("\r\n")
        else:
            split_data = data.split("\r\n")
            self.incomplete_buffer = split_data.pop(-1)
        for line in split_data:
            if line:
                if line.startswith('PING'):
                    parameters = line.split()
                    pong = 'PONG ' + parameters[1]
                    self.send(pong)
                    self.lock.release()
                    return
                eyercbot.send('process message', self.name, line)
        self.lock.release()


class IdentServer(threading.Thread):
    """
    Ident server. Some voodoo
    """
    def __init__(self, userid="EyeRCBot3", nick="EyeRCBot3", port=113):
        threading.Thread.__init__(self)
        self.daemon = True
        self.host = ''
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.on = False
        self.userid = userid
        self.nick = nick
        
    def run(self):
        self.on = True
        self.reactor()
        
    def reactor(self):
        data = None
        while self.on:
            try:
                conn, addr = self.socket.accept()
                data = conn.recv(1024)
            except socket.error:
                pass
            if data:
                split_data = data.split()
                ident = str(data[3]).encode("utf-8") + b" , " + str(data[2]).encode("utf-8") +\
                b" : USERID : " + self.userid.encode("utf-8") + b" : " + self.nick.encode("utf-8")
                conn.send(ident)
            time.sleep(0.1)
                
    def stop(self):
        #self.socket.shutdown(socket.SHUT_RDWR)
        self.on = False
        self.socket.close()

def new_connection(name, server, port):
    connections[name] = IRCConnection(name, server, port)

def connect(connection, *args):
    connections[connection].connect(*args)
    
def connect_all(*args, **kargs):
    #print(*args)
    #print(connections)
    for connection in connections:
        #print('Connection:', connections, args)
        connections[connection].connect(*args, **kargs)

def start(conenction):
    #connections[conenction].run()
    connections[conenction].start()

def start_all():
    for connection in connections:
        #connections[connection].run()
        connections[connection].start()

def send(server, line, encode="utf-8"):
    connections[server].send(line, encode=encode)

def quit(server, message = '', delete=True):
    connections[server].send('QUIT :' + message +'\r\n')
    connections[server].running=False
    log.info('Killing conenction: ' + server)
    log.info('Reason: ' + message)
    if delete:
        del connections[server]

def quit_All(message = ''):
    global connections
    for connection in connections:
        quit(connection, message, delete=False)
    connections = {}

eyercbot.messenger.add('add connection', new_connection)
eyercbot.messenger.add('connect all', connect_all)
eyercbot.messenger.add('connect', connect)
eyercbot.messenger.add('start server', start)
eyercbot.messenger.add('start all', start_all)
eyercbot.messenger.add('send', send)
eyercbot.messenger.add('quit', quit)
eyercbot.messenger.add('quitAll', quit_All)