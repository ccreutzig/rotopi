from time import time, sleep
from RPi import GPIO
from threading import Thread

class RotaryHook(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(18, GPIO.FALLING, callback=self.rotary_pulse)
        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(24, GPIO.BOTH, callback=self.hook, bouncetime=25)

        self.last_rotary_pulse = time()
        self.rotary_pulse_counter = 0
        self.queue = queue

        self.daemon = True

    def hook(self, channel):
        if GPIO.input(24):
            self.queue.put(['hook_up'])
        else:
            self.queue.put(['hook_down'])

    def check_last_rotary_pulse(self):
        if (time() - self.last_rotary_pulse) > 0.25 and self.rotary_pulse_counter > 0:
            self.queue.put(['dialed', str(self.rotary_pulse_counter % 10)])
            self.rotary_pulse_counter = 0

    def rotary_pulse(self, channel):
        self.check_last_rotary_pulse()
        if (time() - self.last_rotary_pulse) >= 0.09:
            self.rotary_pulse_counter += 1
            self.last_rotary_pulse = time()

    def run(self):
        while 1:
            sleep(0.5)
            self.check_last_rotary_pulse()
