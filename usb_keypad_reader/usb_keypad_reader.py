'''
Created on Jan 30, 2018

@author: martin
'''
import sys
from reader import reader
from termcolor import cprint
import threading
import time
from pyfiglet import figlet_format



class USBKeypadReader(reader.Reader):
    '''
    Reader of bib numbers (strings) from standard input. 
    '''

    # The buffer with bib IDs
    buffer = []
    # 10' of security margin to send the values to the server
    SECURITY_MARGIN_SECONDS = 5

    def __init__(self):
        '''
        Constructor
        '''
        pass
        
    def initialize(self):
        '''
        Initializes the reader
        '''
        pass
    
    def sendBufferPeriodically(self):
        '''
        Method that sends the buffer every SECURITY_MARGIN_SECONDS seconds
        It's executed in a separate thread
        '''
        counter = 0
        now = time.time();
        for bib in self.buffer:
            if (now > bib['timestamp'] + self.SECURITY_MARGIN_SECONDS):
                counter += 1
                offset = int(now - bib['timestamp'])
                self.processCallback(None, bib['bib'].strip(), offset=offset)
        self.buffer = self.buffer[counter:]
        threading.Timer(self.SECURITY_MARGIN_SECONDS, self.sendBufferPeriodically).start()


    def printBuffer(self):
        textToReturn = '[ '
        for bib in self.buffer:
            textToReturn += bib['bib'] + ' '
        textToReturn += ']'
        print (textToReturn)


    def doInventory(self, processCallback):
        '''
        Process of inventory execution. After the reader is initialized, an infinite loop is executed waiting for a 
        bib number finished by <intro> 
        :param processCallback(epcID, bibID): callback function to process a bibID found during inventory (epcID=None).
        '''
        self.sendBufferPeriodically();
        self.processCallback = processCallback
        while True:
            bibId = ''
            while bibId.strip() == '':
                self.printBuffer()
                bibId = input('\nBib number? > ')
                if bibId == 'quit':
                    sys.exit()
                if bibId == '--':
                    if len(self.buffer) > 0:
                        # Removes the previous entry in the buffer
                        cprint(figlet_format('--'+self.buffer[-1]['bib'], font='small'), 'white', 'on_red', attrs=['bold'])
                        self.buffer = self.buffer[:-1]
                    bibId = ''
                elif ('-' in bibId) or ('*' in bibId):
                    cprint(figlet_format('BIB NO SET!!', font='small'), 'white', 'on_red', attrs=['bold'])        
                    bibId = ''
            cprint(figlet_format(bibId, font='starwars'), 'white', 'on_green', attrs=['bold'])
            self.buffer += [{ 'bib': bibId, 'timestamp': time.time() }]

