import RPi.GPIO as gpio
import time 

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD) # Using the pin numbers (inside) instead of GPIO (outside)
	
motor_1 = {"e":11,"f":15,"r":13}
motor_2 = {"e":22,"f":16,"r":18}
motor_3 = {"e":19,"f":21,"r":23}
motor_4 = {"e":32,"f":24,"r":26}

def init(motor):
	gpio.setmode(gpio.BOARD)

	gpio.setup(motor["e"], gpio.OUT)
	gpio.setup(motor["f"], gpio.OUT)
	gpio.setup(motor["r"], gpio.OUT)

	pwm = gpio.PWM(motor["e"], 50)
	pwm.start(0)
	motor["pwm"] = pwm

	gpio.output(motor["e"], True)
	gpio.output(motor["e"], False)
	gpio.output(motor["e"], False)
	return 
	

def forward(motors, speed, second):
	for motor in motors:
		init(motor)
		motor["pwm"].start(0)
		time.sleep(2)
		gpio.output(motor["f"], True)
		gpio.output(motor["r"], False)
	for motor in motors:
		motor["pwm"].ChangeDutyCycle(speed)

	time.sleep(second)

	for motor in motors:
		motor["pwm"].stop()
	
	gpio.cleanup()

def backward(motors, speed, second):
	for motor in motors:
		init(motor)
		motor["pwm"].start(0)
		time.sleep(2)
		gpio.output(motor["f"], False)
		gpio.output(motor["r"], True)
		motor["pwm"].ChangeDutyCycle(speed)

	time.sleep(second)

	for motor in motors:
		motor["pwm"].stop()
	
	gpio.cleanup()

def refill(motors, vol):
	norm_speed = 1.427 # 1.5 mL/s at DC=100, f=50.
	duration = vol/norm_speed
	forward(motors, 100, duration)
	
def drain(motors, vol):
	norm_speed = 1.427 # 1.5 mL/s at DC=100, f=50.
	duration = vol/norm_speed
	backward(motors, 100, duration)

def refill_all(vol):
	motors = [motor_1,motor_2,motor_3,motor_4]
	refill(motors, vol)

def drain_all(vol):
	motors = [motor_1,motor_2,motor_3,motor_4]
	drain(motors, vol)
	
#refill([motor_1], 50)

	

