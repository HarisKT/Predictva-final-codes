import serial, string, time
import RPi.GPIO as gpio
import smbus
import time
import sys
import datetime
import smbus
from datetime import datetime
import RPi.GPIO as GPIO
from time import sleep
from firebase import firebase
from functools import partial
import urllib2, urllib, httplib
import json
import os
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD)

#x=0

ser = serial.Serial('/dev/ttyUSB0', 9600)
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8

GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(10, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)
firebase = firebase.FirebaseApplication('your firebase database ', None)

#firebase = firebase.FirebaseApplication('https://temperature-i2c.firebaseio.com/',None)
#def update_firebase():
#    #global x
#    #x+=1
#    data = {"temp": temperature,"volt":voltage}
#    firebase.post('/UART', data)
def spi():
    GPIO.output(10, GPIO.HIGH)
    GPIO.output(18, GPIO.LOW)
    GPIO.output(22, GPIO.LOW)
    print ('Enter NO: 1 for Current')
    print ('Enter NO: 0 for Voltage')
    AO_pin = int(input("enter the sensor:"))
    def init():
              GPIO.setwarnings(False)
              GPIO.setmode(GPIO.BCM)
              # set up the SPI interface pins
              GPIO.setup(SPIMOSI, GPIO.OUT)
              GPIO.setup(SPIMISO, GPIO.IN)
              GPIO.setup(SPICLK, GPIO.OUT)
              GPIO.setup(SPICS, GPIO.OUT)
              pass

    #read SPI data from MCP3008(or MCP3204) chip,8 possible adc's (0 thru 7)
    def readadc(adcnum, clockpin, mosipin, misopin, cspin):
            if ((adcnum > 7) or (adcnum < 0)):
                    return -1
            GPIO.output(cspin, True)  

            GPIO.output(clockpin, False)  # start clock low
            GPIO.output(cspin, False)     # bring CS low

            commandout = adcnum
            commandout |= 0x18  # start bit + single-ended bit
            commandout <<= 3    # we only need to send 5 bits here
            for i in range(5):
                    if (commandout & 0x80):
                            GPIO.output(mosipin, True)
                    else:
                            GPIO.output(mosipin, False)
                    commandout <<= 1
                    GPIO.output(clockpin, True)
                    GPIO.output(clockpin, False)

            adcout = 0
            # read in one empty bit, one null bit and 10 ADC bits
            for i in range(12):
                    GPIO.output(clockpin, True)
                    GPIO.output(clockpin, False)
                    adcout <<= 1
                    if (GPIO.input(misopin)):
                            adcout |= 0x1

            GPIO.output(cspin, True)
            
            adcout >>= 1       # first bit is 'null' so drop it
            return adcout

    def volt():
             init()
             time.sleep(2)
             print"will detect voltage"
             file = open("/home/pi/csvFB/Voltage.csv", "a")
             if os.stat("/home/pi/csvFB/Voltage.csv").st_size == 0:
                        file.write("Date,Time,Voltage\n")
             def update_firebase():
                    data = {"Voltage": a}
                    firebase.post('/SPI/Voltage', data)
             while True:
                      global a
                      ad_value = readadc(AO_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
                      voltage= ad_value*(3.3/1024)*5
                      a=voltage
                      print "***********"
                      print " Voltage is: " + str("%.2f"%a)+"V"
                      print"***********"
                      print' '
                      time.sleep(1)
                      update_firebase()
                      global i
                      i=0
                      i=i+1
                      now = datetime.now()
                      date1=now.date()
                      time1=now.time()
                      file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                      file.flush()

    def current():
             init()
             time.sleep(2)
             print"will detect Current"
             file = open("/home/pi/csvFB/Current.csv", "a")
             if os.stat("/home/pi/csvFB/Current.csv").st_size == 0:
                        file.write("Date,Time,Current\n")
             def update_firebase():
                    data = {"Current": a}
                    firebase.post('/SPI/Current', data)
             while True:
                      #ad_value = readadc(AO_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
                      global a
                      global adcvalue
                      global sensitivity
                      sensitivity=66
                      global offsetvolt
                      offsetvolt=2500
                      global adcvolt
                      global currentvalue
                     # voltage= ad_value*(3.3/1024)*5
                      adcvalue = readadc(AO_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
                      adcvolt=(adcvalue/1024.0)*5000
                      currentvalue=(adcvolt-offsetvolt)/sensitivity
                      print "***********"
                      print " current is: " + str("%.2f"%currentvalue)
                      print"***********"
                      print' '
                      a=currentvalue
                      time.sleep(1)
                      update_firebase()
                      global i
                      i=0
                      i=i+1
                      now = datetime.now()
                      date1=now.date()
                      time1=now.time()
                      file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                      file.flush()


    if __name__ =='__main__':
             try:
                     
                      if (AO_pin==1):
                          current()
                      else:
                          volt()
             except KeyboardInterrupt:
                      pass
    GPIO.cleanup() 

def uart():
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(10, GPIO.LOW)
    GPIO.output(22, GPIO.LOW)
    print ('Enter NO: 1 for Temperature')
    print ('Enter NO: 2 for Voltage')
    print ('Enter NO: 3 for Current')
    print ('Enter NO: 4 for Vibration')
    n=int(input("enter the sensor :"))
    def temp1():
        file = open("/home/pi/csvFB/Temperature.csv", "a")
        if os.stat("/home/pi/csvFB/Temperature.csv").st_size == 0:
                        file.write("Date,Time,Temperature\n")
        def update_firebase():
                    data = {"Temperature": a}
                    firebase.post('/UART/Temperature', data)
        while True:           
                if ser.in_waiting > 0:
                    rawserial = ser.readline()
                    cookedserial = rawserial.decode('utf-8').strip('\r\n')
                    datasplit = cookedserial.split(',')
                    temperature = datasplit[0].strip('<')
                    voltage = datasplit[1].strip('>')
                    current = datasplit[2].strip('@')
                    vibration = datasplit[3].strip('$')
                    a=temperature
                    print(a)
                    update_firebase()
                    global i
                    i=0
                    i=i+1
                    now = datetime.now()
                    date1=now.date()
                    time1=now.time()
                    file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                    file.flush()
    def voltage1():
        file = open("/home/pi/csvFB/Voltage.csv", "a")
        if os.stat("/home/pi/csvFB/Voltage.csv").st_size == 0:
                        file.write("Date,Time,Voltage\n")
        def update_firebase():
                    data = {"Voltage": a}
                    firebase.post('/UART/Voltage', data)
        while True:
                if ser.in_waiting > 0:
                    rawserial = ser.readline()
                    cookedserial = rawserial.decode('utf-8').strip('\r\n')
                    datasplit = cookedserial.split(',')
                    temperature = datasplit[0].strip('<')
                    voltage = datasplit[1].strip('>')
                    a=voltage
                    current = datasplit[2].strip('@')
                    vibration = datasplit[3].strip('$')
                    print(a)
                    update_firebase()
                    global i
                    i=0
                    i=i+1
                    now = datetime.now()
                    date1=now.date()
                    time1=now.time()
                    file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                    file.flush()
    
    def CURRENT1():
        file = open("/home/pi/csvFB/Current.csv", "a")
        if os.stat("/home/pi/csvFB/Current.csv").st_size == 0:
                        file.write("Date,Time,Current\n")
        def update_firebase():
                    data = {"Current": a}
                    firebase.post('/UART/Current', data)
        while True:
                if ser.in_waiting > 0:
                    rawserial = ser.readline()
                    cookedserial = rawserial.decode('utf-8').strip('\r\n')
                    datasplit = cookedserial.split(',')
                    temperature = datasplit[0].strip('<')
                    voltage = datasplit[1].strip('>')
                    current = datasplit[2].strip('@')
                    vibration = datasplit[3].strip('$')
                    a=current
                    print(a)
                    update_firebase()
                    global i
                    i=0
                    i=i+1
                    now = datetime.now()
                    date1=now.date()
                    time1=now.time()
                    file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                    file.flush()
    def vibration1():
        file = open("/home/pi/csvFB/vibration.csv", "a")
        if os.stat("/home/pi/csvFB/vibration.csv").st_size == 0:
                        file.write("Date,Time,vibration\n")
        def update_firebase():
                    data = {"vibration": a}
                    firebase.post('/UART/vibration', data)
        while True:
                if ser.in_waiting > 0:
                    rawserial = ser.readline()
                    cookedserial = rawserial.decode('utf-8').strip('\r\n')
                    datasplit = cookedserial.split(',')
                    temperature = datasplit[0].strip('<')
                    voltage = datasplit[1].strip('>')
                    current = datasplit[2].strip('@')
                    vibration = datasplit[3].strip('$')
                    a=vibration
                    print(a)
                    update_firebase()
                    global i
                    i=0
                    i=i+1
                    now = datetime.now()
                    date1=now.date()
                    time1=now.time()
                    file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                    file.flush()
    
    if __name__ =='__main__':
         try:

              if (n==1):
                  temp1()
              elif(n==2):
                  voltage1()
              elif(n==3):
                  CURRENT1()
              elif(n==4):
                  vibration1()
         except KeyboardInterrupt:
              pass
    GPIO.cleanup() 

def i2c():
    GPIO.output(22, GPIO.HIGH)
    GPIO.output(10, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    bus = smbus.SMBus(1)
    address = 0x08
    temp=""
    print ('Enter NO: 1 for Temperature')
    print ('Enter NO: 2 for Voltage')
    print ('Enter NO: 3 for Current')
    n=int(input("Enter the Value:"))
    def temperature():
            file = open("/home/pi/csvFB/Temperature.csv", "a")
            if os.stat("/home/pi/csvFB/Temperature.csv").st_size == 0:
                            file.write("Date,Time,Temperature\n")
            def update_firebase():
                        data = {"Temperature": a}
                        firebase.post('/I2C/Temperature', data)
            while 1:
                bus.write_byte(address,  ord("1"))
                temp="".join(map(chr,bus.read_i2c_block_data(address,0,5)))
                a=temp
                print ("temp:", a)
                time.sleep(1)
                update_firebase()
                global i
                i=0
                i=i+1
                now = datetime.now()
                date1=now.date()
                time1=now.time()
                file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                file.flush()
    
                
    def voltage():
             file = open("/home/pi/csvFB/Voltage.csv", "a")
             if os.stat("/home/pi/csvFB/Voltage.csv").st_size == 0:
                        file.write("Date,Time,Voltage\n")
             def update_firebase():
                    data = {"Voltage": a}
                    firebase.post('/I2C/Voltage', data)
             while 1:
                bus.write_byte(address,  ord("2"))
                volt="".join(map(chr,bus.read_i2c_block_data(address,0,4)))
                a=volt
                print ("voltage:", a)
                time.sleep(1)
                update_firebase()
                global i
                i=0
                i=i+1
                now = datetime.now()
                date1=now.date()
                time1=now.time()
                file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                file.flush()
    
                
    def current():
            file = open("/home/pi/csvFB/Current.csv", "a")
            if os.stat("/home/pi/csvFB/Current.csv").st_size == 0:
                            file.write("Date,Time,Current\n")
            def update_firebase():
                        data = {"Current": a}
                        firebase.post('/I2C/Current', data)
            while 1:
                bus.write_byte(address,  ord("3"))
                Current="".join(map(chr,bus.read_i2c_block_data(address,0,5)))
                a=Current
                print ("current:", a)
                time.sleep(1)
                update_firebase()
                global i
                i=0
                i=i+1
                now = datetime.now()
                date1=now.date()
                time1=now.time()
                file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                file.flush()
                
    def vibration():
            file = open("/home/pi/csvFB/vibration.csv", "a")
            if os.stat("/home/pi/csvFB/vibration.csv").st_size == 0:
                            file.write("Date,Time,vibration\n")
            def update_firebase():
                        data = {"vibration": a}
                        firebase.post('/I2C/vibration', data)
            while 1:
                bus.write_byte(address,  ord("4"))
                vibe="".join(map(chr,bus.read_i2c_block_data(address,0,5)))
                a=vibe
                print ("vibration:", a)
                update_firebase()
                global i
                i=0
                i=i+1
                now = datetime.now()
                date1=now.date()
                time1=now.time()
                file.write(str(date1)+","+str(time1)+","+str(a)+"\n")
                file.flush()

        
    if __name__ == '__main__':
        try:
            
            if(n==1):
               temperature()
            elif(n==2):
               voltage()
            elif(n==3):
               current()
            else:
               vibration()
        except KeyboardInterrupt:
            print ('Interrupted')
            gpio.cleanup()
            sys.exit(0)



if __name__ =='__main__':
         try:
                  print ('Enter NO: 1 for SPI')
                  print ('Enter NO: 2 for UART')
                  print ('Enter NO: 3 for I2C')
                  protocol=int(input("Enter the protocol :"))             
                  if (protocol==1):
                      print ('Initializing SPI.............')
                      spi()
                  elif (protocol==2):
                      print ('Initializing UART............')
                      uart()
                  elif(protocol==3):
                      print ('Initializing I2C.............')
                      i2c()
         except KeyboardInterrupt:
                  pass
GPIO.cleanup()


