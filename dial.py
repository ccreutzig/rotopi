from time import time, sleep
import thread
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
# GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_pulse = time()
pulse_counter = 0
dialed = ''


def check_last_pulse():
    global last_pulse, pulse_counter, dialed
    if (time() - last_pulse) > 0.25 and pulse_counter > 0:
        dialed += str(((pulse_counter + 1) / 2) % 10)
        pulse_counter = 0


def my_callback(channel):
    global last_pulse, pulse_counter
    check_last_pulse()
    pulse_counter += 1
    last_pulse = time()


def watcher():
    global dialed, last_pulse
    while 1:
        sleep(0.5)
        check_last_pulse()
        if time() - last_pulse > 2.5 and dialed != '':
            print dialed
            dialed = ''


thread.start_new_thread(watcher, ())

GPIO.add_event_detect(18, GPIO.RISING, callback=my_callback, bouncetime=25)

try:
    print "Waiting for rising edge on port 24"
    GPIO.wait_for_edge(24, GPIO.RISING)
    print "Rising edge detected on port 24. Here endeth the third lesson."

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
