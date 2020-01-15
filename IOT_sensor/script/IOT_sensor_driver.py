# -*- coding: utf-8 -*-
from bh1750 import BH1750
from Adafruit_BME280 import *
from Adafruit_SHT31 import *
import aliyunsdkiotclient.AliyunIotMqttClient as iot_ali
import json
import adafruit_ccs811
import SDL_Pi_HDC1000
import paho.mqtt.client as mqtt

import board
import busio
import smbus
import time

options = {
    'productKey':'',
    'deviceName':'',
    'deviceSecret':'',
    'port':1883,
    'host':'iot-as-mqtt.cn-shanghai.aliyuncs.com'
}

host = options['productKey']+'.'+options['host']
air_temp_offset = 5

class IOT_sensor:
    def __init__(self):
        
        bus = smbus.SMBus(1) 
        self.bh1750 = BH1750(bus)
        self.bme280 = BME280(p_mode=BME280_OSAMPLE_8, t_mode=BME280_OSAMPLE_2, h_mode=BME280_OSAMPLE_1, filter=BME280_FILTER_16)
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ccs811 = adafruit_ccs811.CCS811(i2c)
        self.hdc1000 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()
        self.hdc1000.turnHeaterOn()
        self.hdc1000.setTemperatureResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
        self.hdc1000.setHumidityResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT)
        self.sht31 = SHT31(address = 0x44)

        print ("start")
        
    def read_bh1750(self):
        data = []
        ##print (sensor.mtreg)
        for measurefunc, name in [(self.bh1750.measure_low_res, "Low Res "),
                                  (self.bh1750.measure_high_res, "HighRes "),
                                  (self.bh1750.measure_high_res2, "HighRes2")]:
            data.append("%.2f" % measurefunc())
        ##self.bh1750.set_sensitivity((self.bh1750.mtreg + 10) % 255)
        return data
    
    def read_bme280(self):
        degrees = self.bme280.read_temperature()
        pascals = self.bme280.read_pressure()/100   
        return (["%.2f" %degrees,"%.2f" %pascals])
        
    def read_ccs811(self):
        co2 = self.ccs811.eco2
        return (str(co2))
    
    def read_hdc100(self):
        temp = "%3.1f" % self.hdc1000.readTemperature()
        humidity = "%3.1f" % self.hdc1000.readHumidity()
        return ([temp, humidity])
    
    def read_sht35(self):
        temp = "%3.1f" % self.sht31.read_temperature()
        humidity = "%3.1f" % self.sht31.read_humidity()
        return ([temp, humidity])
    
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))

if __name__=="__main__":
    iot = IOT_sensor()
    client = iot_ali.getAliyunIotMqttClient(options['productKey'], options['deviceName'], options['deviceSecret'], secure_mode=3)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host=host, port=options['port'], keepalive=60)
    data_to_update = {}
    topic = '/sys/'+options['productKey']+'/'+options['deviceName']+'/thing/event/property/post'
    while True:
        light = iot.read_bh1750()
        bme = iot.read_bme280()
        ccs = iot.read_ccs811()
        hdc100 = iot.read_hdc100()
        sht35 = iot.read_sht35()
        data_to_update = {
                          'id':int(time.time()),
                          'params':{
                              'light':float(light[1]),
                              'co2':float(ccs),
                              'air_temperature':(float(bme[0])-air_temp_offset),
                              'air_humidity':float(hdc100[1]),
                              'air_pressure':float(bme[1]),
                              'soil_temperature':float(sht35[0]),
                              'soil_humidity':float(sht35[1])},
                          'method': "thing.event.property.post"
                          }        
        client.publish(topic,payload = str(data_to_update),qos=1)

        print (data_to_update)
        time.sleep(10)
        client.loop_start()
