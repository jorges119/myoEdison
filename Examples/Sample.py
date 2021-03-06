import myo
import time

#----------------------------------------
# Spread fingers to exit the application
#----------------------------------------

n=myo.myMyo("E1:23:E9:52:9F:DB")
n.setVibration(myo.myMyo.vibration["MEDIUM"])

while True:
    imu = n.getImuData()
    print ("Acc X: ", imu["AX"])
    print ("Acc Y: ", imu["AY"])
    print ("Acc Z: ", imu["AZ"])
    pose = n.getPoseData()["POSE"]
    if pose == myo.myMyo.pose["FIST"]:
	print "Fist Closed"
    elif pose == myo.myMyo.pose["FINGERS__SPREAD"]:   
        break
    time.sleep(0.5)

n.disconnect()
