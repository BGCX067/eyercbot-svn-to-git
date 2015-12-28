# Hello world plugin
# Each plugin requires three functions
# on_load() will execute when the module is loaded
# on_unload() will be executed when unloaded (such as scheduling events)
# index() is called when the user calls the plugin by !filename

def on_load(connection):
	pass

def on_unload(connection, event):
	pass

# Define index function
def index(connection, event, channels):
	connection.privmsg(event.source().split ( '!' ) [ 0 ], 'Hello world.  I am an IRC bot built in python.')
	connection.privmsg(event.source().split ( '!' ) [ 0 ], 'I am modular and can load command modules on the fly!')
