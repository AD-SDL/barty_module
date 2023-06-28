import RPi.GPIO as gpio
import time 

gpio.setwarnings(False)
gpio.setmode(gpio.BCM) # Using GPIO numbers (outside) not the pin numbers (inside)
	
def init():
	gpio.setmode(gpio.BCM) # Using GPIO numbers (outside) not the pin numbers (inside)
	gpio.setup(23, gpio.OUT) # Motor A, CCW.
	gpio.setup(24, gpio.OUT) # Motor A, CW.
	gpio.setup(5, gpio.OUT) # Motor B, CW.
	gpio.setup(6, gpio.OUT) # Motor B, CCW.
	gpio.setup(12, gpio.OUT) # Motor A
	gpio.setup(13, gpio.OUT) # Motor B

gpio.setup(12, gpio.OUT) # Motor A
gpio.setup(13, gpio.OUT) # Motor B
pwmA = gpio.PWM(12, 50) # Motor A, PWM.
pwmB = gpio.PWM(13, 50) # Motor B, PWM.
pwmA.start(0)
pwmB.start(0)

def forward(motor, speed, second):
	init()
	if "A" in motor:
		pwmA.start(0)
		time.sleep(2)
		gpio.output(23, False)
		gpio.output(24, True)
		pwmA.ChangeDutyCycle(speed)
		time.sleep(second)
		pwmA.stop()
	else:
		pwmB.start(0)
		time.sleep(2)
		gpio.output(5, True)
		gpio.output(6, False)
		pwmB.ChangeDutyCycle(speed)
		time.sleep(second)
		pwmB.stop()
	gpio.cleanup()
	
def backward(motor,speed, second):
	init()
	if "A" in motor:
		pwmA.start(0)
		time.sleep(2)
		gpio.output(23, True)
		gpio.output(24, False)
		pwmA.ChangeDutyCycle(speed)
		time.sleep(second)
		pwmA.stop()
	else:
		pwmB.start(0)
		time.sleep(2)
		gpio.output(5, False)
		gpio.output(6, True)
		pwmB.ChangeDutyCycle(speed)
		time.sleep(second)
		pwmB.stop()
	gpio.cleanup()

def refill(motor, vol):
	norm_speed = 1.427 # 1.5 mL/s at DC=100, f=50.
	duration = vol/norm_speed
	forward(motor, 100, duration)
	
def drain(motor, vol):
	norm_speed = 1.427 # 1.5 mL/s at DC=100, f=50.
	duration = vol/norm_speed
	backward(motor, 100, duration)
	

	

