"""MYO armband (by Thalmic Labs) Python interface for Intel Edison"""
import btle
import struct
import time

class myMyo:
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
    imu_data = { "W": 0,
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
    event_data = {  "INDEX": 0,
		    "COUNT": 0,
    }
    pose_data = {	"ARM": 0,
			"DIR": 0,
			"POSE": 0,
    }
	
    __newIMU = False
    __newEvent = False
    __newPose = False
	
    def __init__(self, deviceAddr=None):
        if deviceAddr is not None:
            global __conn
            __conn = btle.Peripheral(deviceAddr)
            __conn.setDelegate(self)
	    #Turn On Notifications for IMU????-----------------------------------------------
            __conn.writeCharacteristic(0x001d, struct.pack('<bb', 0x01, 0x00))
	    #Event
            __conn.writeCharacteristic(0x0020, struct.pack('<bb', 0x02, 0x00))
            #Classifier
            __conn.writeCharacteristic(0x0024, struct.pack('<bb', 0x02, 0x00))
	    #---------------------------------------------------------------------------------
            #Ask for data (No EMG but acc, gyr...)
            __conn.writeCharacteristic(0x0019, struct.pack('<bbb', 1, 3, 0, 3, 1))

    class notificationHandler(btle.DefaultDelegate):
        def handleNotification(self, cHandle, data):
            if cHandle == 28:
                #print 'IMU data---------------' 
                global imu_data
                received = struct.unpack('hhhhhhhhhh',data)
                imu_data["W"] = received[0] / ori_scale
                imu_data["X"] = received[1] / ori_scale
                imu_data["Y"] = received[2] / ori_scale
                imu_data["Z"] = received[3] / ori_scale
                imu_data["AX"]  = received[4] / acc_scale
                imu_data["AY"]  = received[5] / acc_scale
                imu_data["AZ"]  = received[6] / acc_scale
                imu_data["GR"]  = received[7] / gyr_scale
                imu_data["GP"]  = received[8] / gyr_scale
                imu_data["GY"]  = received[9] / gyr_scale
				
                global __newIMU
                __newIMU = True
	 
            elif cHandle == 35:
                global pose_data
	        #print "Classifier Data---------"
                received = struct.unpack('bbb',data)
                if received[0] == 3:
                    pose_data["POSE"] = received[1]
                    global __newPose
                    __newPose = True
                elif received[0] == 1:
                    pose_data["ARM"] = received[1]
                    pose_data["DIR"] = received[2]
                    global __newPose
                    __newPose = True

                elif cHandle == 31:
                    global event_data
		    #print "Event Data---------"
                    received = struct.unpack('bbb',data)
                    event_data["INDEX"] = received[1]
                    event_data["COUNT"] = received[2]
                    global __newEvent
                    __newEvent = True
				
			

    def getIMUdata(self):
        global __conn
        global __newIMU
		
        __newIMU = False
        while __newIMU == False:
            __conn.waitForNotifications(1.0)
		
        global imu_data
        return imu_data

    def getPosedata(self):
        global __conn
        global __newPose
		
        __newPose = False
        while __newPose == False:
            __conn.waitForNotifications(1.0)	

        global pose_data
        return pose_data

    def getEventdata(self):
        global __conn
        global __newEvent
		
        __newEvent = False
        while __newEvent == False:		
            __conn.waitForNotifications(1.0)
			
        global event_data
        return event_data

	# XXX TODO populate function for reading raw EMG data	
    #def getEMGdata(self):
	#global __conn
        #__conn.waitForNotifications(1.0)

    def setVibration(self, length=1):
        global __conn
        if (length == 1) or (length == 2) or (length == 3):
            __conn.writeCharacteristic(0x0019, struct.pack('<bbb', 3, 1, length))
            time.sleep(1)
        
    def stayAwake(self):
        global __conn
        __conn.writeCharacteristic(0x0019, struct.pack('<bbb', 9, 1, 1))
        time.sleep(0.5)
		
    def disconnect(self):
        global __conn
	try: 
            __conn.writeCharacteristic(0x0019, struct.pack('<bbb', 9, 1, 1))
            time.sleep(0.5)
	    #Turn Off Notifications for IMU????----------------------------------------------
            __conn.writeCharacteristic(0x001d, struct.pack('<bb', 0x00, 0x00))
	    #Event
            __conn.writeCharacteristic(0x0020, struct.pack('<bb', 0x00, 0x00))
	    #Classifier
            __conn.writeCharacteristic(0x0024, struct.pack('<bb', 0x00, 0x00))
            #---------------------------------------------------------------------------------
        finally:
            __conn.disconnect()
			
    def __del__(self):
        global __conn
        __conn.disconnect()

 