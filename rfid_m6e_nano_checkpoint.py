'''
Created on Oct 27, 2018

@author: martin

Main function to run a checkpoint using a M6E nano RFID Reader

'''

from checkpoint import checkpoint
import context
import argparse
from m6e_nano_reader import m6e_nano_reader   


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('serial', help='Serial port (check it with python3 -m serial.tools.list_ports)')
    parser.add_argument('device', help='The ID of the device (string)')
    parser.add_argument('broker', help='MQTT broker hostname')
    parser.add_argument('power', help='Read power in cent-dBi (e.g. 500 or 2600)')
    args = parser.parse_args()
    reader = m6e_nano_reader.M6eNanoReader(args.serial, baud=115200, antenna=1, arg.power)
    checkpoint = checkpoint.Checkpoint(args.device, reader, args.broker)
    checkpoint.execute()
