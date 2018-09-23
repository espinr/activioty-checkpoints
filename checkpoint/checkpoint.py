# -*- coding: utf-8 -*-

'''
Created on Jan 30, 2018

@author: martin
'''
from distutils.command.check import check
import json
import sys
import math
import threading
import logging
from colorama import init
from termcolor import cprint
from pyfiglet import figlet_format
from time import ctime
from time import gmtime
import time

import ntplib
import urllib.request

import paho.mqtt.publish as publish   


class Checkpoint(object):
    
    TOPIC_READY     = 'ready'
    TOPIC_CHECKIN   = 'checkin'
    
    def __init__(self, id, reader, mqttBrokerHost, mqttBrokerPort=1883):
        '''
        :param id: String with the identifier of the Checkpoint
        :param reader: Ind903Reader object (or other Reader) that will do the inventory
        :param mqttBrokerHost: String with the hostname of the MQTT broker
        :param mqttBrokerPort: (int) with the port of the MQTT broker (1883 by default)
        :param loggingFilename: String with the path of the logs file 
        '''
        init(strip=not sys.stdout.isatty())
        self.id = id
        filename = id+'.log'
        logging.basicConfig(filename=filename,level=logging.INFO)
        logging.info('------------------------------------------')
        logging.info('Init ' + id + ' on ' + mqttBrokerHost)
        logging.info('------------------------------------------')
        self.reader = reader
        self.mqttBrokerHost = mqttBrokerHost
        self.mqttBrokerPort = mqttBrokerPort
        if self.isInternetEnabled():
            self.timestampOffset = self.getOffsetNTPTime()
        else:
            self.timestampOffset = 0
            cprint(figlet_format('Working offline!', font='small'), 'yellow', 'on_red', attrs=['bold'])


    def isInternetEnabled(self):
        '''
        Method to check if a URL is reachable. 
        :returns True if a URL is reachable, False otherwise.
        '''
        try:
            urllib.request.urlopen('http://google.com', timeout=1)
            return True
        except Exception as err: 
            return False

    def checkinCompetitor(self, idCompetitorEPC, idCompetitorBibNumber, offset=0):
        '''
        Method to be called once a competitor do a check-in. 
        This is a callback method to be send to the reader. 
        It sends a MQTT message to the broker like this:
        {"checkpoint" : {"id" : "RFID_IND903"}, "timestamp" : 1536508802, "bib": "121"}
        :param idCompetitor: String with the ID of the competitor that the reader detected.
        :param offset: Number of seconds to be subtracted to the timestamp. This is used in 
        case there is a forced security delay (i.e., manual input to be corrected on the fly)  
        '''            
        messageCheckin = { "checkpoint": { "id": self.id }, "timestamp": self.getTimestamp()-offset }
        if (idCompetitorEPC != None):
            messageCheckin["epc"] = idCompetitorEPC; 
        if (idCompetitorBibNumber != None):
            messageCheckin["bib"] = idCompetitorBibNumber;

        topic = self.id + "/" + self.TOPIC_CHECKIN
        try:
            publish.single(topic, json.dumps(messageCheckin), hostname=self.mqttBrokerHost)
            logging.info(json.dumps(messageCheckin))
        except Exception as err:
            print ('Loggin locally')
            logging.error(json.dumps(messageCheckin))
        #print(topic + " topic to MQTT:")
        #print(json.dumps(messageCheckin))

    def pingReadyMessages(self):
        '''
        Method that sends a ready message to the broker every 30"
        Ready message like this:   {"checkpoint" : {"id" : "001"}, "timestamp" : 1535524129}
        It's executed in a separate thread
        '''
        messageReady = { "checkpoint": { "id": self.id } , "timestamp" : self.getTimestamp() }  
        topic = self.id + "/" + self.TOPIC_READY
        try:
            publish.single(topic, json.dumps(messageReady), hostname=self.mqttBrokerHost)
        except Exception as err:
            print ('Still offline...')
        threading.Timer(30, self.pingReadyMessages).start()
        
    def execute(self):
        self.pingReadyMessages()
        self.reader.initialize()
        cprint(figlet_format(self.id, font='doom'), 'yellow', 'on_blue', attrs=['bold'])
        self.reader.doInventory(self.checkinCompetitor)

    def getOffsetNTPTime(self):
        '''
        Get timestamp from a NTP server and stores the offset with the internal clock.
        :return: (float) with the difference between the local clock and the NTP time (in seconds)
        '''
        c = ntplib.NTPClient()
        response = c.request('europe.pool.ntp.org', version=3)
        # convert from seconds since 1900 to seconds since 1970
        ntpUnixtime = response.tx_timestamp - 2208988800
        timestampOffset = time.time() - ntpUnixtime;
        return timestampOffset 

    def getTimestamp(self):
        '''
        Returns the local time plus the offset registered at the beginning.
        :return: long with the current timestamp (unix time)
        '''
        return int(time.time() + self.timestampOffset)

