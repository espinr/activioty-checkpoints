'''
Created on Oct 27, 2018

@author: martin

Main function to run a checkpoint using a M6E nano RFID Reader

'''

from __future__ import print_function
import time
import sys
import mercury


if __name__ == '__main__':
    reader = mercury.Reader("tmr:///dev/ttyUSB0", baudrate=115200)
    reader.set_region("EU3")
    reader.set_read_plan([1], "GEN2", read_power=500)
    reader.start_reading(lambda tag: print(tag.epc, tag.antenna, tag.read_count, tag.rssi))
    while 1:
        message = input('reading tags, type "quit" to exit...')
        if message == 'quit' or message == 'exit':
            reader.stop_reading()
            sys.exit()
