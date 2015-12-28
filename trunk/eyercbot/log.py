import logging
import logging.handlers
log = logging.getLogger("BotLogs")
LEVEL = 0
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

def configure(path, level_name):
    level = LEVELS.get(level_name, logging.NOTSET)
    log.setLevel(level)
    global LEVEL 
    LEVEL = level
    handler = logging.handlers.RotatingFileHandler(
              path, maxBytes=1048576, backupCount=5)
    log.addHandler(handler)
    stream = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    stream.setFormatter(formatter)
    log.addHandler(stream)
    log.info('Logging stream handler added.')
    info("Configured logger")

def screen(message):
    '''Attempts to print message to screen. However Microsoft sucks and wont update cmd to support unicode.'''
    try:
        print(message[0:200])
        pass
    except:
        log.warning("Unable to output to terminal:", message)
        print("Unable to print line in this terminal")

def build(args):
    message = ""
    #print(args)
    for a in args:
        message = message + str(a) + " "
    return message[:-1]

def debug(*args):
    #print("a")
    #print(args)
    message = build(args)
    log.debug(message)
    #if LEVEL >= 10: screen(message)
def info(*args):
    #print("b")
    #print(args)
    message = build(args)
    log.info(message)
    #if LEVEL >= 20: screen(message)
def warning(*args):
    message = build(args)
    log.warning(message)
    #if LEVEL >= 30: screen(message)
def error(*args):
    message = build(args)
    log.error(message)
    #if LEVEL >= 40: screen(message)
def critical(*args):
    message = build(args)
    log.critical(message)
    #if LEVEL >= 50: screen(message)
def exception(*args):
    message = build(args)
    log.exception(message)
