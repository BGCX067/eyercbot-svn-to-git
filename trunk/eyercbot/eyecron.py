'''
Not to be confused with anything resembling cron.
I just needed a cool name for the scheduler system.
This is based on http://code.google.com/p/scheduler-py but suited for my needs
All time is in utc
'''

import datetime, threading, operator, time
import eyercbot
import logging
log = logging.getLogger("EyercCron")

eyercbot.scheduler = None

class UTC(datetime.tzinfo):
    """UTC"""
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO

utc = UTC()

class Task(threading.Thread):
    '''Stores information needed to run a task.'''
    def __init__(self, name, start_time, frequency, function, arguments=[], run_once=False):
        '''frequency and start_time is string as "DD:HH:MM:SS"
        start time is a datetime instance for the day the function should occcure
        run_once will be looked at in the schduler and task will be deleted after being run
        Threaded for your pleasure
        '''
        threading.Thread.__init__(self)
        self.name = name
        self.start_time = start_time
        self.scheduled_time = start_time
        self.frequency = frequency
        self.function = function
        self.arguments = arguments
        self.run_once = run_once
    
    def run(self):
        '''Scheduler will run this function'''
        try:
            self.function(self.arguments)
        except:
            raise
        if not self.run_once:
            # Remember scheduled_time is the old scheduled time
            self.scheduled_time = self.computeTime(self.scheduled_time, self.frequency)
    
    def computeTime(self, now, future="00:00:00:01"):
        '''Computes next scheduled time
        now must be a datetime object, future is our string format
        '''
        days, hours, minutes, seconds = future.split(":")
        return now + datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))


    # In case I forget. The scheduler will sort by scheduled time and then wait for the duration until scheduled time. adding a new task will need to redo the scheduling process
class Scheduler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.tasks = {}
        self.tasks_lock = threading.Lock()
        self.running = True
        self.not_empty = threading.Event()
        self.halt_flag = threading.Event()
        log.info("Scheduler started")
    
    def add(self, name, start_time, frequency, function, arguments=[], run_once=False):
        self.tasks_lock.acquire()
        self.tasks[name] = Task(name, start_time, frequency, function, arguments, run_once)
        self.tasks_lock.release()
        self.not_empty.set()
        self.halt_flag.set()
        log.info("Schduled " + name)
    
    def delete(self, name):
        self.tasks_lock.acquire()
        try:
            del self.tasks[name]
        except:
            print("Invalid task name to delete:", name)
        self.tasks_lock.release()
        self.halt_flag.set()
    
    def findNextTask(self):
        '''Finds next task and returns name'''
        self.tasks_lock.acquire()
        by_time = lambda x: operator.getitem(x, 1).scheduled_time
        items = list(self.tasks.items())
        items.sort(key=by_time)
        try:
            name = items[0][0]
        except:
            name = None
        self.tasks_lock.release()
        return name
        
    def computeWait(self):
        '''Computes the wait time for the thread. Updated upon addition and deletion of entries as well.'''
        task_name = self.findNextTask()
        if task_name:
            task_time = self.tasks[task_name].scheduled_time
            wait_time = task_time - datetime.datetime.utcnow()
            seconds_to_wait = 0
            if wait_time > datetime.timedelta():
                seconds_to_wait = wait_time.seconds
        else:
            seconds_to_wait = None
        return seconds_to_wait
        
    def run(self):
        while self.running:
            task_name = self.findNextTask()
            seconds_to_wait = self.computeWait()
            self.halt_flag.wait(seconds_to_wait)
            try:
                if task_name:
                    # In order to reprocess wait times we need to make sure it is time to run
                    log.debug("Running Task: " + task_name)
                    self.tasks_lock.acquire()
                    task = self.tasks[task_name]
                    if task.scheduled_time <= datetime.datetime.utcnow():
                        task.run()
                    self.tasks_lock.release()
            except:
                raise
            time.sleep(0.5)

def makeScheduler():
    eyercbot.scheduler = Scheduler()
    eyercbot.scheduler.start()