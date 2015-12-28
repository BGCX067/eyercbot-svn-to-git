'''Database.  Usefull for group and user databases.'''

import glob
import yaml

class Database:
    '''Database class which stores and manages database.
    self.databaseis the actual database
    self.path is the file path (string) to the files.  Ends with trailing slash
    self.prototype is the prototype class that populates the database.  yes it must be a class'''
    def __init__(self, prototype, path):
        self.database = {}
        self.path = path
        self.prototype = prototype
        print(self.path, self.prototype)
        self.loadAll()
        print("Database for", prototype, "loaded.")
    
    def loadAll(self):
        '''Loads all entries from path.'''
        # We scan the user folder and load them into a dictionary
        # Issues with directories (ie .svn).  Look into os.walk?
        for source in glob.glob ( self.path + '*.yaml' ):
            name = source.replace ( '.yaml', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
            self.load(name)
    
    def load(self, name):
        '''Loads an individual entry into the database. If "all" is passed then loadAll is called instead.'''
        if name.lower() == 'all':
            self.loadAll()
            return
        entryFile = open(self.path + name + '.yaml')
        stream = entryFile.read()
        entryFile.close()
        self.database[name.lower()] = yaml.load(stream)
        print("Loaded", self.prototype, name)
    
    def saveAll(self):
        '''Saves all database entries to file.'''
        for entry in self.database:
            stream = file(self.path + entry + '.yaml', 'w')
            yaml.dump(self.database[entry.lower()], stream)
            stream.close()
    
    def save(self, name):
        '''Saves an indivudal entry to file. If "all" is passed then saveAll is called instead.'''
        if name.lower() == 'all':
            self.saveAll()
            return
        stream = open(self.path + name + '.yaml', 'w')
        yaml.dump(self.database[name.lower()], stream)
        stream.close()
    
    def makeEntry(self, name):
        '''Checks to see if the entry exists and if not, makes it.'''
        if name.lower() not in self.database:
            self.database[name.lower()] = self.prototype(name)
    
    def findEntry(self, name):
        '''
        Searches database for entry by name.
        Returns object pointer if found. None if not.
        '''
        if name.lower() in self.database:
            return self.database[name.lower()]
        else:
            return None