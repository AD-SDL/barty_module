import RPi.GPIO as gpio
import time 

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD) # Using the pin numbers (inside) instead of GPIO (outside)
motors= {"motor_1":{"e":11,"f":15,"r":13}, "motor_2":{"e":22,"f":16,"r":18}, "motor_3":{"e":19,"f":21,"r":23}, "motor_4":{"e":32,"f":24,"r":26}}

def init(motor):
	gpio.setmode(gpio.BOARD)

	gpio.setup(motors[motor]["e"], gpio.OUT)
	gpio.setup(motors[motor]["f"], gpio.OUT)
	gpio.setup(motors[motor]["r"], gpio.OUT)

	pwm = gpio.PWM(motors[motor]["e"], 50)
	pwm.start(0)
	motors[motor]["pwm"] = pwm

	gpio.output(motors[motor]["e"], True)
	gpio.output(motors[motor]["e"], False)
	gpio.output(motors[motor]["e"], False)
	return 
	

def forward(lis_motors, speed, second):
	for motor in lis_motors:
		init(motors[motor])
		motors[motor]["pwm"].start(0)
		time.sleep(2)
		gpio.output(motors[motor]["f"], True)
		gpio.output(motors[motor]["r"], False)
		motors[motor]["pwm"].ChangeDutyCycle(speed)

	time.sleep(second)

	for motor in lis_motors:
		motors[motor]["pwm"].stop()
	
	gpio.cleanup()

def backward(lis_motors, speed, second):
	for motor in lis_motors:
		init(motors[motor])
		motors[motor]["pwm"].start(0)
		time.sleep(2)
		gpio.output(motors[motor]["f"], False)
		gpio.output(motors[motor]["r"], True)
		motors[motor]["pwm"].ChangeDutyCycle(speed)

	time.sleep(second)

	for motor in lis_motors:
		motors[motor]["pwm"].stop()
	
	gpio.cleanup()

def refill(lis_motors, vol):
	norm_speed = 1.427 # 1.5 mL/s at DC=100, f=50.
	duration = vol/norm_speed
	forward(lis_motors, 100, duration)
	
def drain(lis_motors, vol):
	norm_speed = 1.427 # 1.5 mL/s at DC=100, f=50.
	duration = vol/norm_speed
	backward(lis_motors, 100, duration)

def refill_all(vol):
	lis_motors = ["motor_1","motor_2","motor_3","motor_4"]
	refill(lis_motors, vol)

def drain_all(vol):
	lis_motors = ["motor_1","motor_2","motor_3","motor_4"]
	drain(lis_motors, vol)


	

	

