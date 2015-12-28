"""
A module for scheduling arbitrary callables to run at given times
or intervals, modeled on the naviserver API.  Scheduler runs in
its own thread; callables run in this same thread, so if you have
an unusually long callable to run you may wish to give it its own
thread, for instance,

schedule(3600, lambda: threading.Thread(target=longcallable).start())

Scheduler does not provide subsecond resolution.

Public functions are threadsafe.
"""
# import scheduler
# help(scheduler)


import atexit, sys, threading, time, traceback


# My code(for when the schedule is itself a plugin)
#def on_load():
#	pass
#
#def on_unload():
#	pass
# /My code

logger = lambda s: sys.stderr.write('%s\n' % s)
def debuglogger(*args):
    #import spyce
    #spyce.log.debug(*args)
	pass

def schedule(connection, interval, callable, once=False):
    """
    Schedules callable to be run every interval seconds.
    Returns the scheduled Task object.
    """
    if interval < 1:
        raise Exception("Interval must be postitive")
    return _insertsorted(Task(connection, time.time() + interval, interval, callable, once))

def _nearest_epoch(hours, minutes):
    L = list(time.localtime(time.time()))
    L[3] = hours
    L[4] = minutes
    L[5] = 0
    epoch = time.mktime(L)
    if epoch < time.time():
        epoch += 24 * 3600
    return epoch

def schedule_daily(connection, hours, minutes, callable, once=False):
    """
    Schedules callable to be run at hours:minutes every day.
    (Hours is a 24-hour format.)
    Returns the scheduled Task object.
    """
    if hours > 23 or hours < 0:
        raise ValueError("Invalid hours %s" % hours)
    if minutes > 59 or minutes < 0:
        raise ValueError("Invalid minutes %s" % minutes)
    epoch = _nearest_epoch(hours, minutes)
    return _insertsorted(Task(connection, epoch, 24 * 3600, callable, once))

def schedule_weekly(connection, day, hours, minutes, callable, once=False):
    """
    Schedules callable to be run at hours:minutes on the given
    zero-based day of the week.  (Monday is 0.)
    Returns the scheduled Task object.
    """
    if day > 6 or day < 0:
        raise ValueError("Invalid day %s" % day)
    if hours > 23 or hours < 0:
        raise ValueError("Invalid hours %s" % hours)
    if minutes > 59 or minutes < 0:
        raise ValueError("Invalid minutes %s" % minutes)
    epoch = _nearest_epoch(hours, minutes)
    while time.localtime(epoch)[6] != day:
        epoch += 24 * 3600
    return _insertsorted(Task(connection, epoch, 7 * 24 * 3600, callable, once))

def unschedule(task):
    """
    Removes the given task from the scheduling queue.
    """
    _qlock.acquire()
    try:
        _queue.remove(task)
    finally:
        _qlock.release()

class Task:
    """
    Instantiated by the schedule methods.
    
    Instance variables:
      nextrun: epoch seconds at which to run next
      interval: seconds before repeating
      callable: function to invoke
      last: if True, will be unscheduled after nextrun

    (Note that by manually setting last on a Task instance, you
    can cause it to run an arbitrary number of times.)
    """
    def __init__(self, connection, firstrun, interval, callable, once):
	self.connection = connection
        self.nextrun = firstrun
        self.interval = interval
        self.callable = callable
        self.last = once
    def __repr__(self):
        return 'Task(nextrun=%r, interval=%d, callable=%s, last=%s)' \
               % (time.asctime(time.localtime(self.nextrun)), self.interval, self.callable, self.last)

_qlock = threading.RLock()
# (we don't use a Queue object here since we need to do our own locking anyway)
_queue = []

def _insertsorted(task):
    _qlock.acquire()
    i = len(_queue)
    while i > 0:
        if task.nextrun < _queue[i - 1].nextrun:
            break
        i -= 1
    _queue.insert(i, task)
    _qlock.release()
    return task

_keepgoing = True
_paused = False

def _process():
    """True if a task was run"""
    try:
        _qlock.acquire()
        if not len(_queue):
            return False
        if _queue[-1].nextrun > time.time():
            return False
        task = _queue.pop()
    finally:
        _qlock.release()
    debuglogger('running scheduled task %s', task.callable)
    try:
        #task.callable()
	task.callable(task.connection) # More of my code, sends the connection information to the function in case it is needed to message the server
    except Exception:
        logger(traceback.format_exc())
    if not task.last:
        task.nextrun = max(task.nextrun + task.interval, time.time())
        _insertsorted(task)
    return True

def _loop():
    sleep = False
    while _keepgoing:
        if sleep:
            time.sleep(1)
        if _paused:
            sleep = True
            continue
        sleep = not _process()
    debuglogger("Scheduler thread has stopped")

_thread = threading.Thread(target=_loop, name='spyce-scheduler')
_thread.start()

def pause():
    """Temporarily suspend running scheduled tasks"""
    _paused = True
    
def unpause():
    """
    Resume running scheduled tasks.  If a task came due while
    it was paused, it will run immediately after unpausing.
    """
    _paused = False

def _cleanup():
    debuglogger('Waiting for scheduler thread...')
    global _keepgoing
    _keepgoing = False
    _thread.join()
    
atexit.register(_cleanup)

# yes, I need more and better tests...  you're welcome to add some :)
if __name__ == "__main__":
    d = {}
    def foo():
        d['test'] = 1
    print schedule(1, lambda: threading.Thread(target=foo).start(), True)
    while not d:
        time.sleep(1)
    print d
    assert not _queue

    d = {}
    hours, minutes, _, day = time.localtime(time.time() + 61)[3:7]
    print schedule_weekly(day, hours, minutes, foo)
    print '(waiting...  could be up to 60 seconds)'
    while not d:
        time.sleep(1)
    print d
    assert len(_queue) == 1
    


