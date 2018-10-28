
import RPi.GPIO as gpio
import time
import subprocess

gpio.setmode(gpio.BOARD)

flow_switch=12
pump=11
float_switch=13

gpio.setup(flow_switch, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pump, gpio.OUT)
gpio.setup(float_switch, gpio.IN, pull_up_down=gpio.PUD_DOWN)

log=open("/home/jannie/borehole_log.txt","a")
log.write("Device restarted\n\n")
log.close()

time.time()
bash_date="date +%d-%m-%y_%H-%M-%S"
full=False
pumping=False


def tank_full(flowing):
	gpio.output(pump, False)
	if (flowing):
			stop_time=time.time()
			log=open("/home/jannie/borehole_log.txt","a")
			log.write(" pumped for "+str(round(stop_time-start_time))+" seconds\n\n")
			log.close()
	full_time = subprocess.check_output(bash_date.split())[:-1];
	log = open("/home/jannie/borehole_log.txt", "a")
	log.write("Main Tank Full: "+full_time+"\n\n")
	log.close()
	print("Main tank full")##debug**
	while not gpio.input(float_switch):
		time.sleep(300)##Wait 5 minutes.


def start_pump():
	global start_time
	global pumping
	gpio.output(pump, True)
	pumping=True
	start_time=time.time()
	log = open("/home/jannie/borehole_log.txt", "a")
	pump_time = subprocess.check_output(bash_date.split())[:-1];
	log.write("Start pumping at "+pump_time+"\n")
	log.close()
	print("Pumping")##debug**
	time.sleep(10)


def stop_pump():
	gpio.output(pump, False)
	stop_time=time.time()
	log = open("/home/jannie/borehole_log.txt", "a")
	log.write(" pumped for "+str(round(stop_time-start_time))+" seconds\n\n")
	log.close()
	print("Stopped pumping")##debug**


def run():
	time.sleep(5)
	print("float_switch=",gpio.input(float_switch))##debug**
	print("flow_switch=",gpio.input(flow_switch))##debug**
	global pumping
	while(True):
		if not gpio.input(float_switch):
			tank_full(False)
			continue
		start_pump()
		while(pumping):
			if not gpio.input(float_switch):
				pumping=False
				tank_full(True)
				break

			if not gpio.input(flow_switch):
				time.sleep(2)
				if not gpio.input(flow_switch):
					pumping=False
					stop_pump()
					time.sleep(900)


run()
