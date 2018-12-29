#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from reader import reader
import sys
import traceback
import binascii
import mercury
import _thread

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
        self.nano = None

    def initialize(self):
        self.nano = mercury.Reader(self.portName, baudrate=115200)
        self.nano.set_region(self.region)
        self.nano.set_read_plan([self.antenna], self.tagsType, read_power=self.readPower)
        print(self.nano.get_power_range())
        print(self.nano.get_model())
        print(self.nano.get_read_powers())
        self.previousEpc = ""

    def processTags(self, tags, processCallback):
        """
        Process the readed tags.
        :param tags: array of TagReadData with the EPCs (in tags[x].epc) readed
        :param processCallback(epcID, bibID): callback function to process a EPC found during inventory (bib=None).
        """
        for tag in tags:
            epc = tag.epc.decode("utf-8")
            validEPC = epc[:8] 
            # It expects only the first 8 chars -> Change this to allow any EPC
            print (' [EPC: ' + validEPC + ']')
            print(validEPC)
            processCallback(validEPC, None)

    def doInventory(self, processCallback):
        """
        Process of inventory execution. After the reader is initialized, an infinite loop is executed waiting for:
        the user to type quit or exit.
        :param processCallback(epcID, bibID): callback function to process a EPC found during inventory (bib=None).
        """
        print("Reading tags...")
        while True:
            try:
                tags = self.nano.read()
                if (len(tags) > 0):
                    _thread.start_new_thread(self.processTags, (tags, processCallback))
            except Exception as e:
                print(e)

        
