'''
Created on Jan 29, 2018

@author: martin

Main function to run a checkpoint using a IND903 RFID Reader

'''

from checkpoint import checkpoint
import context
import argparse
from ind903_reader import ind903_reader   


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('serial', help='Serial port (check it with python3 -m serial.tools.list_ports)')
    parser.add_argument('device', help='The ID of the device (string)')
    parser.add_argument('broker', help='MQTT broker hostname')
    args = parser.parse_args()
    reader = ind903_reader.Ind903Reader(args.serial, 115200)
    checkpoint = checkpoint.Checkpoint(args.device, reader, args.broker)
    checkpoint.execute()
