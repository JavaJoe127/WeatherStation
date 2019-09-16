import RPi.GPIO as GPIO
import Adafruit_BMP.BMP085 as BMP085
import dht11
import time
import datetime
import logging

global fahrenheit
global celsius
global humidity
global pressure
global altitude
global dht_stream
global bmp_stream
global time_stamp

def bigNum():
    return 999

def initLogger(logfile):
    try:
        logging.shutdown()
    except:
        print("Error in Shutdown File: " + str(logfile))
    print("New File: " + str(logfile))
    
    logging.basicConfig(filename=logfile,
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m-%d-%Y %I:%M:%S %p')
    first_line = "Begin logging data at " + str(datetime.datetime.now())
    logging.info(first_line)
    logging.info("Data Format: (Celsius, Fahrenheit, Pressure - inhg, Humidity)")

def initDisplay():
    print("Begin logging data at {:%Y-%m-%d %H:%M:%S}" .format(datetime.datetime.now()))
    print("Data Format: (Celsius, Fahrenheit, Pressure, Humidity)")

def logData(time_stamp, info_stream, humidity):
    temp_stream = info_stream[0], info_stream[1], info_stream[2], humidity
    logging.info(temp_stream)
    print("{0:%Y-%m-%d %H:%M:%S} {1[0]}, {1[1]}, {1[2]}, {1[3]}" .format(time_stamp, temp_stream))

def feq(a,b):
    epsilon = EPSILON
    if abs(a-b) < epsilon:
        return True
    else:
        return False

def readDHT():
    retry = True
    try:
        result = dht.read()
        if result.is_valid():
            humidity = result.humidity
            celsius = result.temperature
            fahrenheit = round(celsius * 1.8 + 32,1)
        else:
            logging.debug("invalid result from DHT")
            humidity = bigNum()

    except:
        logging.debug("error reading DHT")
        humidity = bigNum()

    return humidity
    
def readBMP():
    try:
        hPa = bmp.read_pressure()
        celsius = round(bmp.read_temperature(),1)
        # convert to f and round to int
        fahrenheit = round(celsius * 1.8 + 32,1)

        # convert hPa (hectoPascals) to inHg (inches of mercury)
        # normalize and add 5.32 to compensate for altitude in Albuquerque, NM
        pressure = round(((hPa * 0.0295301) / 100) + 5.32,2)
        bmp_stream = celsius, fahrenheit, pressure
        return bmp_stream
    except:
        logging.info("error reading BMP")
        return None

def loopReadSensors():
    prev_date = "2018-01-01"
    prev_humid = bigNum()
    prev_bmp = bigNum()
    
    while True:
        try:
            curr_date = datetime.datetime.now()
            date = str(curr_date)[0:10]

            # new logfile each day
            if date != prev_date:
                initLogger(date)
                initDisplay()
                prev_date = date

            # read devices
            humidity = readDHT()
            if humidity == bigNum():
                humidity = prev_humid
            else:
                prev_humid = humidity
            
            bmp_stream = readBMP()
            if bmp_stream is not None:
                if bmp_stream != prev_bmp:
                    time_stamp = datetime.datetime.now()
                    logData(time_stamp, bmp_stream, humidity)
                    prev_bmp = bmp_stream
                if prev_bmp == bigNum():
                    prev_bmp = bmp_stream
            
            time.sleep(10)
        except KeyboardInterrupt:
            break
        except:
            logging.debug("error in loopReadSensors data stream = {0[0]}, {0[1]}, {0[2]}, {1}".format(bmp_stream, humidity))

if __name__ == "__main__":

    # initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()

    fahrenheit = 0.0
    celsius = 0
    humidity = 0
    pressure = 0

    # init dht using pin 14
    dht = dht11.DHT11(pin=23)
    # init bmp
    bmp = BMP085.BMP085()

    # main loop
    loopReadSensors()


