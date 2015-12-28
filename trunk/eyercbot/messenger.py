'''messenger.py
Threaded messenger for internal communication'''
import eyercbot.log as log
import threading

# messages = {'message string': [{'function': function, 'threading': bool}, {'function2': function2, 'threading': bool}}
# Threading signals if the function should be threaded or not
# The dict may be replaced by a small class if additional functionality is needed
db = {}

# Simple lock to prevent thead issues
lock = threading.Lock()


def add(name, function, threaded = False):
    '''Adds a new message to be listened to. If the message exists we append'''
    lock.acquire()
    if name not in db:
        db[name] = [{'function': function, 'threaded': threaded}]
        log.debug("Added " + name + " to messenger.")
    else:
        db[name].append({'function': function, 'threaded': threaded})
        log.debug("Appended " + name + " to messenger.")
    lock.release()

def delete(name, function):
    '''Removes selected function from message system'''
    lock.acquire()
    if name in db:
        for listener in db[name]:
            if listener['function'] == function:
                db[name].remove(listener)
                log.debug("Removed " + str(function) + " from " + name)
                if not listener['function']:
                    del db[name]
                    log.debug("Removed " + name + " from messenger.")
    lock.release()

def delete_all(name):
    '''Removes the entire message from the listening system'''
    lock.acquire()
    if name in db:
        del db[name]
        log.debug("Removed " + name + " from messenger.")
    lock.release()

def send(message, *args, **kwargs):
    '''Sends the message, to all listening things'''
    #lock.acquire()
    if message in db:
        for item in db[message]:
            if not item['threaded']:
                item['function'](*args, **kwargs)
            elif item['threaded']:
                threading.Thread(target=item['function'], args=args, kwargs=kwargs)
    #lock.release()