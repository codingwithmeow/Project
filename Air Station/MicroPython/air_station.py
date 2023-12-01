# Control an LED and read a Button using a web browser
import time
import network
import socket
from machine import Pin,PWM,ADC
from picobricks import SSD1306_I2C,WS2812, DHT11,NEC_16, IR_RX
from utime import sleep
import utime
import urequests

THINGSPEAK_WRITE_API_KEY = '7VIQUHPB1EY438R2'
HTTP_HEADERS = {'Content-Type': 'application/json'}

buzzer = PWM(Pin(20))

WIDTH = 128
HEIGHT = 64
sda=machine.Pin(4)
scl=machine.Pin(5)
i2c=machine.I2C(0,sda=sda, scl=scl, freq=1000000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

ws = WS2812(6, brightness=0.4)
ws.pixels_fill((0 ,0 ,0 ))
ws.pixels_show()      

pico_temp=DHT11(Pin(11, Pin.IN, Pin.PULL_UP))
current_time=utime.time()
utime.sleep(1)

ssid = "robotistan metro34"
password = "bmc34RbT124"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

oled.text("Power On",30,0)
oled.text("Waiting for ",20, 30)
oled.text("Connection",23, 40)
oled.show()
time.sleep(2)
oled.fill(0)


# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)
    
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    
    
# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)
oled.text("IP",50, 0)
oled.text(str(status[0]),20, 10)
oled.text("Connected",25, 20)
oled.show()
# Listen for connections, serve client
#Servo

if(utime.time() - current_time > 2):
    current_time = utime.time()
    try:
        pico_temp.measure()
    except:
        print("measurement failed, will try again soon")

temperature=pico_temp.temperature
humidity=pico_temp.humidity
   
while True:
    oled.fill(0)
    
    if(utime.time() - current_time > 2):
        current_time = utime.time()
        try:
            pico_temp.measure()
        except:
            print("measurement failed, will try again soon")
            
    oled.fill(0)#clear OLED
    oled.show()
    
    
    temperature=pico_temp.temperature
    humidity=pico_temp.humidity
    
    oled.text("Temp: ",15,0)#print "Temperature: " on the OLED at x=15 y=10
    oled.text(str(int(temperature)),55,0)
    oled.text("Hum: ", 15,10)
    oled.text(str(int(humidity)),55,10)
    oled.show()#show on OLED
    utime.sleep(0.5)#wait for a half second
        
    dht_readings = {'field1':temperature, 'field2':humidity}
    request = urequests.post( 'http://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY, json = dht_readings, headers = HTTP_HEADERS )  
    request.close() 
    print(dht_readings)
    
    if(temperature >= 25):
        ws.pixels_fill((255, 0, 0))
        ws.pixels_show()
    elif(temperature > 10 and temperature < 25):
        ws.pixels_fill((255, 255, 0))
        ws.pixels_show()
    elif(temperature <= 10):
        ws.pixels_fill((0, 0, 255))
        ws.pixels_show()
        
    if (temperature < 4 ):
        oled.text("There is a danger of icing")
        for i in range((3)):
            buzzer.duty_u16(2000)
            buzzer.freq(831)
            time.sleep(0.25) 
    
    buzzer.duty_u16(0)
    time.sleep(0.25)
          
