import time
import RPi.GPIO as gpio
from rpi_ws281x import PixelStrip, Color

# LED strip configuration:
LED_COUNT = 150       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            rainbowCycle(strip)


    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)  # Using the pin numbers (inside) instead of GPIO (outside)
motors = {
    "motor_1": {"e": 11, "f": 15, "r": 13},
    "motor_2": {"e": 22, "f": 16, "r": 18},
    "motor_3": {"e": 19, "f": 21, "r": 23},
    "motor_4": {"e": 32, "f": 24, "r": 26},
}


def init(motor):
    gpio.setmode(gpio.BOARD)

    gpio.setup(motors[motor]["e"], gpio.OUT)
    gpio.setup(motors[motor]["f"], gpio.OUT)
    gpio.setup(motors[motor]["r"], gpio.OUT)

    pwm = gpio.PWM(motors[motor]["e"], 50)
    pwm.start(0)
    motors[motor]["pwm"] = pwm

    gpio.output(motors[motor]["e"], True)
    gpio.output(motors[motor]["f"], False)
    gpio.output(motors[motor]["r"], False)
    return


def forward(lis_motors, speed, second):
    for motor in lis_motors:
        init(motor)
        motors[motor]["pwm"].start(0)
        time.sleep(2)
        gpio.output(motors[motor]["f"], False)
        gpio.output(motors[motor]["r"], True)
        motors[motor]["pwm"].ChangeDutyCycle(speed)
    time.sleep(second)

    for motor in lis_motors:
        motors[motor]["pwm"].stop()

    gpio.cleanup()


def backward(lis_motors, speed, second):
    for motor in lis_motors:
        init(motor)
        motors[motor]["pwm"].start(0)
        time.sleep(2)
        gpio.output(motors[motor]["f"], True)
        gpio.output(motors[motor]["r"], False)
        motors[motor]["pwm"].ChangeDutyCycle(speed)

    time.sleep(second)

    for motor in lis_motors:
        motors[motor]["pwm"].stop()

    gpio.cleanup()


def refill(lis_motors, vol):
    norm_speed = 1.427  # 1.5 mL/s at DC=100, f=50.
    duration = vol / norm_speed
    forward(lis_motors, 100, duration)


def drain(lis_motors, vol):
    norm_speed = 1.427  # 1.5 mL/s at DC=100, f=50.
    duration = vol / norm_speed
    backward(lis_motors, 100, duration)


def refill_all(vol):
    lis_motors = ["motor_1", "motor_2", "motor_3", "motor_4"]
    refill(lis_motors, vol)


def drain_all(vol):
    lis_motors = ["motor_1", "motor_2", "motor_3", "motor_4"]
    drain(lis_motors, vol)
