"""MYO armband (by Thalmic Labs) Python interface for Intel Edison"""
import btle
import struct
import time

class myMyo:
    __conn = None
    imu_data  = None
    event_data = None
    pose_data  = None
    __newIMU  = None
    __newEvent  = None
    __newPose  = None
	
    __ori_scale = 16384.0
    __acc_scale = 2048.0
    __gyr_scale = 16.0 
	
    pose = { "REST": 0,
             "FIST": 1,
             "WAVE__IN": 2,
             "WAVE__OUT": 3,
             "FINGERS__SPREAD": 4,
             "DOUBLE__TAP": 5,
             "UNKNOWN": 0xffff,
    }
    vibration = { "SHORT" : 1,
		  "MEDIUM" : 2,
		  "LONG" : 3,	
    }
	
    def __init__(self, deviceAddr=None):
        if deviceAddr is not None:
            myMyo.imu_data = { "W": 0,
		         "X": 0,
		         "Y": 0,
		         "Z": 0,
		         "AX": 0,
		         "AY": 0,
		         "AZ": 0,
		         "GR": 0,
		         "GP": 0,
		         "GY": 0,
            }
            myMyo.event_data = {  "INDEX": 0,
		            "COUNT": 0,
            }
            myMyo.pose_data = {	"ARM": 0,
	        		"DIR": 0,
	        		"POSE": 0,
            }
            myMyo.__newIMU = False
            myMyo.__newEvent = False
            myMyo.__newPose = False
			
            self.__conn = btle.Peripheral(deviceAddr)
            self.__conn.setDelegate(self)
	        #Turn On Notifications for IMU????-----------------------------------------------
            self.__conn.writeCharacteristic(0x001d, struct.pack('<bb', 0x01, 0x00))
	        #Event
            self.__conn.writeCharacteristic(0x0020, struct.pack('<bb', 0x02, 0x00))
            #Classifier
            self.__conn.writeCharacteristic(0x0024, struct.pack('<bb', 0x02, 0x00))
	        #---------------------------------------------------------------------------------
            #Ask for data (No EMG but acc, gyr...)
            self.__conn.writeCharacteristic(0x0019, struct.pack('<bbb', 1, 3, 0, 3, 1))

    class notificationHandler(btle.DefaultDelegate):
        def handleNotification(self, cHandle, data):
            if cHandle == 28:
                #print 'IMU data---------------' 
                received = struct.unpack('hhhhhhhhhh',data)
                myMyo.imu_data["W"] = received[0] / myMyo.ori_scale
                myMyo.imu_data["X"] = received[1] / myMyo.ori_scale
                myMyo.imu_data["Y"] = received[2] / myMyo.ori_scale
                myMyo.imu_data["Z"] = received[3] / myMyo.ori_scale
                myMyo.imu_data["AX"]  = received[4] / myMyo.acc_scale
                myMyo.imu_data["AY"]  = received[5] / myMyo.acc_scale
                myMyo.imu_data["AZ"]  = received[6] / myMyo.acc_scale
                myMyo.imu_data["GR"]  = received[7] / myMyo.gyr_scale
                myMyo.imu_data["GP"]  = received[8] / myMyo.gyr_scale
                myMyo.imu_data["GY"]  = received[9] / myMyo.gyr_scale
				
                myMyo.__newIMU = True
	 
            elif cHandle == 35:
	        #print "Classifier Data---------"
                received = struct.unpack('bbb',data)
                if received[0] == 3:
                    myMyo.pose_data["POSE"] = received[1]
                    myMyo.__newPose = True
                elif received[0] == 1:
                    myMyo.pose_data["ARM"] = received[1]
                    myMyo.pose_data["DIR"] = received[2]
                    myMyo.__newPose = True

                elif cHandle == 31:
		            #print "Event Data---------"
                    received = struct.unpack('bbb',data)
                    myMyo.event_data["INDEX"] = received[1]
                    myMyo.event_data["COUNT"] = received[2]
                    myMyo.__newEvent = True
				
			

    def getIMUdata(self):	
        myMyo.__newIMU = False
        while myMyo.__newIMU == False:
            self.__conn.waitForNotifications(1.0)
		
        return myMyo.imu_data

    def getPosedata(self):
        myMyo.__newPose = False
        while myMyo.__newPose == False:
            self.__conn.waitForNotifications(1.0)	

        return myMyo.pose_data

    def getEventdata(self):
        myMyo.__newEvent = False
        while myMyo.__newEvent == False:		
            self.__conn.waitForNotifications(1.0)
			
        return myMyo.event_data

	# XXX TODO populate function for reading raw EMG data	
    #def getEMGdata(self):
        #self.__conn.waitForNotifications(1.0)

    def setVibration(self, length=1):
        if (length == 1) or (length == 2) or (length == 3):
            self.__conn.writeCharacteristic(0x0019, struct.pack('<bbb', 3, 1, length))
            time.sleep(1)
        
    def stayAwake(self):
        self.__conn.writeCharacteristic(0x0019, struct.pack('<bbb', 9, 1, 1))
        time.sleep(0.5)
		
    def disconnect(self):
	try: 
            self.__conn.writeCharacteristic(0x0019, struct.pack('<bbb', 9, 1, 1))
            time.sleep(0.5)
	    #Turn Off Notifications for IMU????----------------------------------------------
            self.__conn.writeCharacteristic(0x001d, struct.pack('<bb', 0x00, 0x00))
	    #Event
            self.__conn.writeCharacteristic(0x0020, struct.pack('<bb', 0x00, 0x00))
	    #Classifier
            self.__conn.writeCharacteristic(0x0024, struct.pack('<bb', 0x00, 0x00))
            #---------------------------------------------------------------------------------
        finally:
            self.__conn.disconnect()
			
    def __del__(self):
        self.__conn.disconnect()

 