#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import traceback
import mercury

class M6eNanoReader(reader.Reader):
        
    def __init__(self, portName, baud=115200, antenna=1, readPower=500):
        """
        :param portName: serial port where the device is mounted (e.g., '/dev/ttyUSB0')
        :param baud: (int) baud rate for communications over the serial port. 
        The baud rates are 9600bps、19200bps、38400bps、115200bps. The default baud rate is 115200bps.
        :param antenna: (int) the id of the antenna (1 by default)
        :param readPower: (integer) reading power from (in cent-dBi)
        """
        self.portName = "tmr://" + portName
        self.antenna = antenna
        self.baud = baud
        self.region = "EU3"
        self.tagsType = "GEN2"
        self.readPower = readPower

    def initialize(self):
            self.reader = mercury.Reader(self.portName, baudrate=self.baud)
            self.reader.set_region(self.region)
            self.reader.set_read_plan([self.antenna], self.tagsType, read_power=self.readPower)
            self.reader.start_reading(lambda tag: print(tag.epc, tag.antenna, tag.read_count, tag.rssi))

    def doInventory(self, processCallback):
        """
        Process of inventory execution. After the reader is initialized, an infinite loop is executed waiting for:
        the user to type quit or exit.
        :param processCallback(epcID, bibID): callback function to process a EPC found during inventory (bib=None).
        """
        while (True):
            try:
                self.reader.start_reading(lambda tag: processCallback(tag.epc, None))
                while True:
                    message = input('type "quit" to exit...')
                    if message == 'quit' or message == 'exit':
                        reader.stop_reading()
                        sys.exit()
            except Exception as ex:
                traceback.print_exc()

#if __name__ == '__main__':
#    reader = Ind903Reader('/dev/ttyUSB0', 115200, 1000)
#    reader.doInventory()
    
        
