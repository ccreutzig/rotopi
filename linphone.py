import subprocess
from select import select
import re
from threading import Thread

class Linphone(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        subprocess.call(['killall', '-9', 'linphonec'])
        self.pipe = subprocess.Popen(["linphonec", "-c", "/home/pi/.linphonerc"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.queue = queue
        self.daemon = True

    def sendDTMF(self, number):
        self.pipe.stdin.write(number)
        self.pipe.stdin.write("\n")

    def answer(self):
        self.pipe.stdin.write("answer\n")

    def hangup(self):
        self.pipe.stdin.write("terminate\n")

    def call(self, number):
        self.pipe.stdin.write("call sip:%s@fritz.fonwlan.box\n" % number)

    def run(self):
        while 1:
            status = select([self.pipe.stdout, self.pipe.stderr], [],
                [self.pipe.stdout, self.pipe.stderr])
            if status[2] != []:
                # error condition, better restart linphonec
                self.pipe.close
                self.pipe = subprocess.Popen("linphonec",
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            line = status[0][0].readline()
            # print(line)
            m = re.search('Receiving new incoming call from (.*),', line)
            if m:
                self.queue.put(['incoming', m.group(1)])
            m = re.search('Call .* with (.*) ended', line)
            if m:
                self.queue.put(['disconnected', m.group(1)])
            m = re.search('Call .* with (.*) connected.', line)
            if m:
                self.queue.put(['connected', m.group(1)])
            m = re.search('User is busy.', line)
            if m:
                self.queue.put(['busy'])
            m = re.search('Call .* with (.*) error\\.', line)
            if m:
                self.queue.put(['error', m.group(1)])
