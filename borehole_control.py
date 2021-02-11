import RPi.GPIO as gpio
import time
import subprocess
import sys
import mysql.connector
from mysql.connector import errorcode

import thread

gpio.setmode(gpio.BOARD)

#borehole
flow_switch=7
pump=11
float_switch=13

gpio.setup(flow_switch, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pump, gpio.OUT)
gpio.output(pump, False) #Make sure borehole pump is off.
gpio.setup(float_switch, gpio.IN, pull_up_down=gpio.PUD_DOWN)

borehole_wait_time = 15 #seconds. Time between turning the borehole pump on and checking to see if water is flowing.
borehole_rest_time = 1800 #seconds => 30min
borehole_max_pump_time=300 #seconds => 5min

borehole_flow_rate = 0.5833 #l/sec (estimated)

start_time=0

#booster
booster_switch=37
flow_rate=1.77 #l/min

gpio.setup(booster_switch, gpio.IN, pull_up_down=gpio.PUD_DOWN)
booster_min_rest_time=30 #min acceptable time between pumps for booster pump.
booster_max_run_time=120 #2 min. Max acceptable time for booster to run for.
control_start_time=""

booster_continuous_alert_sent=False;

time.time()
bash_date="date +%d-%m-%y_%H-%M-%S"
full=False
pumping=False

def errorLog(message):
	error_time = time.time()
	log=open("/home/jannie/borehole_log.txt","a")
	log.write("\n"+str(error_time)+": "+message)
	log.close()

def getConnection():
        connection=None
        try:
                connection = mysql.connector.connect(user="jannie", password="Jackal51", host="127.0.0.1", database="borehole")
        except mysql.connector.Error as err:
                print "Error openning db connection: "+str(err)
        return connection

def closeConnection(connection):
        if(connection!=None):
                try:
                        connection.close()
                except mysql.connector.Error as sql_error:
                        errorLog("SQL Error trying to close db connection: "+str(sql_error))
		except Exception as error:
			errorLog("Error trying to close db connection: "+str(error))

def writeLog(log_code, pump_time, pump_volume, log_message, pump):
	connection = getConnection()
#	+--------------------------+--------------+------+-----+------------------+----------------+
#	| Field                    | Type         | Null | Key | Default          | Extra          |
#	+--------------------------+--------------+------+-----+------------------+----------------+
#	| borehole_log_id          | bigint(20)   | NO   | PRI | NULL             | auto_increment |
#	| borehole_log_pump_time   | int(11)      | YES  |     | NULL             |                |
#	| borehole_log_pump_volume | int(11)      | YES  |     | NULL             |                |
#	| borehole_log_message     | varchar(255) | YES  |     | NULL             |                |
#	| borehole_log_time        | bigint(20)   | NO   |     | unix_timestamp() |                |
#	| borehole_log_code        | int(11)      | NO   | MUL | NULL             |                |
#	+--------------------------+--------------+------+-----+------------------+----------------+

	log_time = time.time()

	insert_log = "INSERT INTO borehole_log (borehole_log_time, borehole_log_code"
	value_placeholders=") VALUES (%s,%s"
	values_list=[log_time, log_code]

	if(pump_time!=None):
		insert_log+=", borehole_log_pump_time"
		value_placeholders+=",%s"
		values_list.append(pump_time)
		if(pump==1): #borehole pump
			pump_volume = round(pump_time*borehole_flow_rate)
	if(pump_volume!=None):
		insert_log+=", borehole_log_pump_volume"
		value_placeholders+=",%s"
		values_list.append(pump_volume)
	if(log_message!=None):
		insert_log+=", borehole_log_message"
		value_placeholders+=",%s"
		values_list.append(log_message)
	if(pump>0):
		insert_log+=", borehole_log_pump"
		value_placeholders+=",%s"
		values_list.append(pump)
	value_placeholders+=")"
	insert_log+=value_placeholders

#	insert_log = "INSERT INTO borehole_log (borehole_log_time, borehole_log_code, borehole_log_pump_time, borehole_log_pump_colume, borehole_log_message) VALUES ("+str(log_time)+","+str(log_code)+","+str(pump_time)+","+str(pump_volume)+","+str(log_message)+")";
#	log_data = (log_time, log_code, pump_time, pump_volume, log_message)
	log_data = tuple(values_list)

	try:
		cursor = connection.cursor()
		cursor.execute(insert_log, log_data)
#		cursor.execute(insert_log)
		print "cursor="+str(cursor)
		connection.commit()
	except mysql.connector.Error as sql_error:
		errorLog("SQL Error while trying to insert borehole log: "+str(sql_error))
	except Exception as error:
		errorLog("Error while trying to insert borehole log: "+str(error))
	finally:
		closeConnection(connection)

def tank_full(flowing):
	global start_time
	gpio.output(pump, False)
	writeLog(4,None, None, "Main tank full",0) #,"Main Tank Full: "+full_time+"\n\n")
	if (flowing):
			stop_time=time.time()
			time_pumping = round(stop_time-start_time)
			writeLog(3,time_pumping, None,"Pumped for "+str(time_pumping)+" seconds",1)
	full_time = subprocess.check_output(bash_date.split())[:-1];
	print("Main tank full") #debug**
	while not gpio.input(float_switch):
		time.sleep(300) ##Wait 5 minutes.


def start_pump():
	global start_time
	global pumping
	gpio.output(pump, True)
	pumping=True
	start_time=time.time()
	pump_time = subprocess.check_output(bash_date.split())[:-1];
	writeLog(2, None, None, "Started pumping at "+pump_time,1)
	print("Pumping") #debug**
	time.sleep(borehole_wait_time)


def stop_pump():
	global start_time
#	print "stop_pump(): start_time="+str(start_time) #debug**
	gpio.output(pump, False)
	stop_time=time.time()
	time_pumping = round(stop_time-start_time)
	writeLog(3,time_pumping, None, "Pumped for "+str(time_pumping)+" seconds",1)
	print("Stopped pumping") #debug**


#booster
def boosterPumpThread(thread_name, delay):
	print "Booster thread started" #debug**
	global gpio
	global start_time
	global booster_switch
	global flow_rate
	global control_start_time
	global booster_continuous_alert_sent
	control_start_time=subprocess.check_output(bash_date.split())[:-1];
	total_volume=0
	booster_pumping=False
	booster_start_time=0
	booster_stop_time=0

	while(True):
		if(gpio.input(booster_switch)==1 and booster_pumping==False):
			booster_start_time=time.time()
			booster_pump_date=subprocess.check_output(bash_date.split())[:-1];

			#Check how long since last pump and create alert if neccessary.
			rest_time = booster_start_time-booster_stop_time;
			if(rest_time<booster_min_rest_time):
				print "Booster rest time is less than "+str(booster_min_rest_time)+" sec"
				writeLog(22, None, None,"Booster rest time is less than "+str(booster_min_rest_time)+"sec!",2);

			writeLog(5, None, None, None,2) #Booster pump started.
			print "Booster pump started" ##debug**
			booster_pumping=True
		elif(gpio.input(booster_switch)==0 and booster_pumping==True):
			booster_continuous_alert_sent=False
			booster_stop_time=time.time()
			elapsed_time=booster_stop_time-booster_start_time
			volume=flow_rate*elapsed_time
			total_volume+=volume
			#Record pumping time and estimated volume.
			print "Booster pump stopped, pumped for ",str(elapsed_time)," volume=",str(volume) ##debug**
			writeLog(6, elapsed_time, volume, "Pumped for "+str(elapsed_time)+", Volume="+str(volume),2)
			#booster_log.write("\n Total volume since "+control_start_time+" ="+str(total_volume))

			#Booster pump has stopped running continuously so update flag.
			#booster_max_run_alert = open("/home/jannie/booster_max_run_time.txt","w")
			#booster_max_run_alert.write("False");
			#booster_max_run_alert.close();

			booster_pumping=False

		#Check if booster pump is just running continuously and alert if necessary.
		elif(gpio.input(booster_switch)==1):
			booster_run_time = time.time()-booster_start_time
			if(booster_run_time>booster_max_run_time and booster_continuous_alert_sent!=True):
				booster_continuous_alert_sent=True
#				booster_max_run_alert = open("/home/jannie/booster_max_run_time.txt","w")
				writeLog(22,None, None, "Booster pump appears to be running continuously!",2)
		time.sleep(0.1)


def run():
	global start_time
	global borehole_rest_time
	global borehole_max_pump_time
	global gpio
	global float_switch
	global flow_switch
	global pumping

	malfunction=False

	time.sleep(5)
	writeLog(1,None, None,"Device restarted",0)

	#booster
	thread.start_new_thread(boosterPumpThread, ("booster_thread1",0))

	print("float_switch=",gpio.input(float_switch)) #debug**
	print("flow_switch=",gpio.input(flow_switch)) #debug**

	try:
		while(True):
			if not gpio.input(float_switch):
				tank_full(False)
				continue
			if gpio.input(flow_switch): ##Flow switch is activated before pump has started, malfunction.
				time.sleep(2)
				if gpio.input(flow_switch):
					if(gpio.input(pump)):
                        			stop_pump()
					malfunction=True
					writeLog(21, None, None, "Flow switch malfunction!",0)
					break
			start_pump()
#			print "run(): start_time="+str(start_time) #debug**
			while(pumping):
				if not gpio.input(float_switch):
#					print "Tank sensed to be full" #debug**
					pumping=False
					tank_full(True)
					break

				if not gpio.input(flow_switch):
					time.sleep(2)
					if not gpio.input(flow_switch):
#						print "water stopped flowing" #debug**
						pumping=False
						stop_pump()
						time.sleep(borehole_rest_time) #900)
				elif(time.time()-start_time>=borehole_max_pump_time):
					malfunction=True
					writeLog(21,None, None, "Borehole pump reached max pump time!",1)
					break
			if malfunction:
				if(gpio.input(pump)):
		                        stop_pump()
				break
	except Exception as error:
		print "Something broke! Check borehole now! Error => "+str(error)
		errorLog("Something broke! Check borehole now! Error => "+str(error))
		writeLog(21, None, None, "Something broke! Check borehole now!",1)
	except:
		errorLog("Something really unknown broke")
	finally:
		if(gpio.input(pump)):
			stop_pump()
		gpio.output(pump, False)
		gpio.cleanup()
		print "pump switched off" #debug**

run()
