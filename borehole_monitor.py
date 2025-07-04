import RPi.GPIO as gpio
import time
import subprocess

gpio.setmode(gpio.BOARD)

flow_switch=12
light = 16

gpio.setup(flow_switch, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(light, gpio.OUT)


start_time=0
stop_time=0
bash_date="date +%d-%m-%y_%H-%M-%S"

while(True):
	gpio.wait_for_edge(flow_switch, gpio.RISING)
	start_time=time.time()
#	gpio.output(light,True)
	log = open("/home/jannie/borehole_log.txt", "a")
	
	pump_time = subprocess.check_output(bash_date.split())[:-1];
	
	log.write("Start pumping at "+pump_time+"\n")
	log.close()
#	print("Pumping")
	time.sleep(10)
	
	if(gpio.input(flow_switch)):
		gpio.wait_for_edge(flow_switch, gpio.FALLING)
		time.sleep(2)

	while(gpio.input(flow_switch)):
		time.sleep(2)

	stop_time=time.time()
#	gpio.output(light,False)
	log = open("/home/jannie/borehole_log.txt", "a")
	log.write(" pumped for "+str(round(stop_time-start_time+2))+" seconds\n\n")
	log.close()
#	print("Stopped pumping")
	
