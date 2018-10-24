# See https://docs.pycom.io for more information regarding library specifics
import pycom
from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE
import time
from network import Sigfox
import socket
#above are imports for the libraries, some are internal some are in the lib folder of this program


pycom.heartbeat(False)#allows led to be controlled by disabling the default mode
def main():
    py = Pysense()#pysense object to pass through to each of the sensor objects 
    si = SI7006A20(py)#object for temperature sensor
    mpp = MPL3115A2(py,mode=PRESSURE)#creates barometer object in pressure mode
    lt=LTR329ALS01(py)#light sensor object
    li=LIS2HH12(py)#creates object for accelerometer

    #Calls funtion to send data to Sigfox 10 times.

    while(True):#runs indefinately
            light=""
            acceleration=""#resets the variables to prevent msg size error
            mData=""
            print(str(acceleration))
            #Gets all data and sends seperate messages
            light = str(lt.light()[0]) + "," +str(lt.light()[1])#sends blue lux and red lux separated
            #acceleration given as X, Y then Z
            accelerationxy = str(round(li.acceleration()[0],1))+","+str(round(li.acceleration()[1],1))
            mData = str(round(si.temperature(),1))+","+str(round(mpp.pressure()/100,1))#dividing pressure by 100 to let it fit in the size constraint
            #print(str(mData))
            #print(str(accelerationxy)) //Prints used when testing the module when it is connected via serial port connection
            #print(light)
            SendSigfox(mData,0xff0000)#Each induvidual message is sent to sigfox with respective data // red flashes
            SendSigfox(accelerationxy,0xffb347)#custom led colours are passed through here // white-blue flashes
            SendSigfox(light,0x0000ff)#blue flashes
            time.sleep(7)#halts processes for 7 seconds to prevent sigfox throttling messages
            
            

    
#Method below will be called to show a physical indication on the module using its led
#allows for colour to be unique and takes param on call
def LedFlash(colour):
    pycom.rgbled(colour) #on
    time.sleep(.5)#sleeping the module for half a second staggers the flashing effect making it better
    pycom.rgbled(0x000000) #off
    time.sleep(.5)
    pycom.rgbled(colour) #on
    time.sleep(.5)
    pycom.rgbled(0x000000) #off
    time.sleep(.5)
    pycom.rgbled(colour) #on
    time.sleep(.5)
    pycom.rgbled(0x000000) #off
    time.sleep(.5)
    pycom.rgbled(0x00ff00)#green led for remainder of the wait
    
    
    
#Method below handles creation of a socket and sending of a message to sigfox
#colour of led is also passed through here
def SendSigfox(message, c):
    #print("sending")//debugging
   
    #initalise Sigfox for RCZ1 (Europe)
    sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
    #create and configure Sigfox socket
    s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
    s.setblocking(True)
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)
    #send message on the socket defined above
    s.send(message)
    LedFlash(c)#run the led flash once sent

    #print("done")//debugging
    
main()#Run The Program via the main function