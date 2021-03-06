"""MYO armband (by Thalmic Labs) Python interface for Intel Edison"""
import btle
import struct
import time

class myMyo:
    __conn = None
    ntfy = None
	
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
			
            self.__conn = btle.Peripheral(deviceAddr)
            self.ntfy = self.notificationHandler()
            self.__conn.setDelegate(self.ntfy)
	        #Turn On Notifications for IMU????-----------------------------------------------
            self.__conn.writeCharacteristic(0x001d, struct.pack('<bb', 0x01, 0x00))
	        #Event
            self.__conn.writeCharacteristic(0x0020, struct.pack('<bb', 0x02, 0x00))
            #Classifier
            self.__conn.writeCharacteristic(0x0024, struct.pack('<bb', 0x02, 0x00))
	        #---------------------------------------------------------------------------------
            #Ask for data (No EMG but acc, gyr...)
            self.__conn.writeCharacteristic(0x0019, struct.pack('<bbbbb', 1, 3, 0, 3, 1))
            time.sleep(1)
            self.stayAwake()

    class notificationHandler(btle.DefaultDelegate):
        __ori_scale = 16384.0
        __acc_scale = 2048.0
        __gyr_scale = 16.0 
			
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

        newIMU = False
        newEvent = False
        newPose = False

        def handleNotification(self, cHandle, data):
            if cHandle == 28:
                #print 'IMU data---------------' 
                received = struct.unpack('hhhhhhhhhh',data)
                self.imu_data["W"] = received[0] / self.__ori_scale
                self.imu_data["X"] = received[1] / self.__ori_scale
                self.imu_data["Y"] = received[2] / self.__ori_scale
                self.imu_data["Z"] = received[3] / self.__ori_scale
                self.imu_data["AX"]  = received[4] / self.__acc_scale
                self.imu_data["AY"]  = received[5] / self.__acc_scale
                self.imu_data["AZ"]  = received[6] / self.__acc_scale
                self.imu_data["GR"]  = received[7] / self.__gyr_scale
                self.imu_data["GP"]  = received[8] / self.__gyr_scale
                self.imu_data["GY"]  = received[9] / self.__gyr_scale
				
                self.newIMU = True
	 
            elif cHandle == 35:
	        #print "Classifier Data---------"
                received = struct.unpack('bbb',data)
                if received[0] == 3:
                    self.pose_data["POSE"] = received[1]
                    self.newPose = True
                elif received[0] == 1:
                    self.pose_data["ARM"] = received[1]
                    self.pose_data["DIR"] = received[2]
                    self.newPose = True

            elif cHandle == 31:
                #print "Event Data---------"
                received = struct.unpack('bbb',data)
                self.event_data["INDEX"] = received[1]
                self.event_data["COUNT"] = received[2]
                self.newEvent = True
			

    def getImuData(self):	
        self.ntfy.newIMU = False
        while self.ntfy.newIMU == False:
            self.__conn.waitForNotifications(1.0)
	
        return self.ntfy.imu_data

    def getPoseData(self):
        self.ntfy.newPose = False
        while self.ntfy.newPose == False:
            self.__conn.waitForNotifications(1.0)	

        return self.ntfy.pose_data

    def getEventData(self):
        self.ntfy.newEvent = False
        while self.ntfy.newEvent == False:		
            self.__conn.waitForNotifications(1.0)
			
        return self.ntfy.event_data

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
            self.__conn.writeCharacteristic(0x0019, struct.pack('<bbb', 9, 1, 0))
	    #Turn Off Notifications for IMU????----------------------------------------------
            #self.__conn.writeCharacteristic(0x001d, struct.pack('<bb', 0x00, 0x00))
	    #Event
            #self.__conn.writeCharacteristic(0x0020, struct.pack('<bb', 0x00, 0x00))
	    #Classifier
            #self.__conn.writeCharacteristic(0x0024, struct.pack('<bb', 0x00, 0x00))
            #---------------------------------------------------------------------------------
        finally:
            self.__conn.disconnect()
			
    def __del__(self):
        self.__conn.disconnect()

 