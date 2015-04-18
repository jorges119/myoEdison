"""Bluetooth Low Energy Python interface"""
import btle
import struct
import time
import tty,sys
import mraa

ori_scale = 16384.0
acc_scale = 2048.0
gyr_scale = 16.0 
rest = 0x0000
fist = 0x0001
wave_in = 0x0002
wave_out = 0x0003
fingers_spread = 0x0004
double_tap = 0x0005
unknown = 0xffff

x=mraa.Pwm(5)
move=0

class NotificationHandler(btle.DefaultDelegate):
    def handleNotification(self, cHandle, data):
	#print "Hi"
        if cHandle == 28:
            #print 'IMU data---------------' 
            received = struct.unpack('hhhhhhhhhh',data)
            w = received[0] / ori_scale
            x = received[1] / ori_scale
            y = received[2] / ori_scale
            z = received[3] / ori_scale
            ax  = received[4] / acc_scale
            ay  = received[5] / acc_scale
            az  = received[6] / acc_scale
            gr  = received[7] / gyr_scale
            gp  = received[8] / gyr_scale
            gy  = received[9] / gyr_scale
            #print ('Orientation', format(w,'.2f'), format(x,'.2f'), format(y,'.2f'), format(z,'.2f'))
            #print ('Acceler', ax, ay, az)
            #print ('Gyroscope', gr, gp, gy)
            
            global move
            move = 1 - abs((w+1)/2)
            #print 1 - abs((w+1)/2)
 
        elif cHandle == 35:
            #print "Classifier Data---------"
            received = struct.unpack('bbb',data)
	    if received[0] == 3:
                pose = received[1]
                print ('Pose:', pose)
            elif received[0] == 1:
		arm = received[1]
                dir = received[2]
		print ('Arm:' , arm)

        elif cHandle == 31:
            print "Event Data---------"
            received = struct.unpack('bbb',data)
            print received

        else:
            print cHandle

conn = btle.Peripheral("E1:23:E9:52:9F:DB")
x.enable(True)
conn.setDelegate(NotificationHandler())

#Stay Awake
#ch.write('\x09\x01\x01')

#Turn On Notifications for IMU????-----------------------------------------------
conn.writeCharacteristic(0x001d, struct.pack('<bb', 0x01, 0x00))
#Event
conn.writeCharacteristic(0x0020, struct.pack('<bb', 0x02, 0x00))
#Classifier
conn.writeCharacteristic(0x0024, struct.pack('<bb', 0x02, 0x00))
#-------------------------------------------------------------------------------

#Write Long Vibration!!!
svc=conn.getServiceByUUID('d5060001-a904-deb9-4748-2c7f4a124842')
ch=svc.getCharacteristics('d5060401-a904-deb9-4748-2c7f4a124842')[0]
ch.write(struct.pack("BBB",3,1,1))
time.sleep(1)
#Ask for data (No EMG but acc, gyr...)
ch.write('\x01\x03\x00\x03\x01')
#for i in range(5):

try:
    while True:
        #if conn.waitForNotifications(1.0):
        #    print "Someone Called" 
        conn.waitForNotifications(1.0)
        x.write(move)
        #time.sleep(0.5)

except KeyboardInterrupt:
    print 'Finished Loop'

#Turn Off Notifications for IMU????----------------------------------------------
conn.writeCharacteristic(0x001d, struct.pack('<bb', 0x00, 0x00))
#Event
conn.writeCharacteristic(0x0020, struct.pack('<bb', 0x00, 0x00))
#Classifier
conn.writeCharacteristic(0x0024, struct.pack('<bb', 0x00, 0x00))
#-------------------------------------------------------------------------------

conn.disconnect()
x.enable(False)

 