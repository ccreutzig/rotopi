import rotaryhook
import linphone
import Queue

# Driving FSA
class PhoneMachine:
    def __init__(self):
        self.eventQueue = Queue.Queue()
        self.linphone = linphone.Linphone(self.eventQueue)
        self.linphone.start()
        self.dialer = rotaryhook.RotaryHook(self.eventQueue)
        self.dialer.start()
        self.dialbuffer = ''
        self.status = self.standby
        while True:
            # print(self.status)
            self.status()

    def get_event(self):
        ret = self.eventQueue.get(True)
        self.eventQueue.task_done()
        # print ret
        return ret

    def get_event_timeout(self,timeout):
        try:
            ret = self.eventQueue.get(True,timeout)
            self.eventQueue.task_done()
            # print ret
            return ret
        except Queue.Empty:
            return ['timeout', timeout]

    # on-hook states
    def standby(self):
        # TODO: stop ringing and playing tones
        self.dialbuffer = ''
        self.linphone.hangup()
        # TODO: check linphone status, maybe restart
        while 1:
            event = self.get_event()
            if event[0] == 'incoming':
                self.status = self.ringing
                break
            if event[0] == 'hook_up':
                self.status = self.dialtone
                break
            if event[0] == 'dialed':
                self.status = self.preCollect
                self.dialbuffer = event[1]
                break

    def preCollect(self):
        preCollectTimeout = 10 # forget collected digits after 10 seconds
        while 1:
            event = self.get_event_timeout(preCollectTimeout)
            if event[0] == 'hook_up':
                self.status = self.initiateCall
                break
            if event[0] == 'dialed':
                self.dialbuffer += event[1]
                break

    def ringing(self):
        # start ringing
        while 1:
            event = self.get_event()
            if event[0] == 'disconnected':
                self.status = self.standby
                break
            if event[0] == 'hook_up':
                self.status = self.inCall
                break
        # stop ringing

    # off-hook states
    def dialtone(self):
        # TODO: start playing dialtone
        while 1:
            event = self.get_event()
            if event[0] == 'hook_down':
                self.status = self.standby
                break
            if event[0] == 'dialed':
                self.status = self.collectingNumber
                self.dialbuffer = event[1]
                break
        # TODO: stop playing dialtone

    def collectingNumber(self):
        collectingNumberTimeout = 2.5
        while 1:
            event = self.get_event_timeout(collectingNumberTimeout)
            if event[0] == 'dialed':
                self.dialbuffer += event[1]
                break
            if event[0] == 'hook_down':
                self.status = self.standby
                break
            if event[0] == 'timeout':
                self.status = self.initiateCall
                break

    def initiateCall(self):
        self.linphone.call(self.dialbuffer)
        # TODO: ensure we have a dial tone
        while 1:
            event = self.get_event() # timeout?
            if event[0] == 'error':
                self.status = self.playError
                break
            if event[0] == 'busy':
                self.status = self.playBusy
                break
            if event[0] == 'hook_down':
                self.status = self.standby
                break
            if event[0] == 'connected':
                self.status = self.inCall
                break
        # TODO: ensure we no longer play a dial tone

    def playError(self):
        # TODO: play some recorded file
        while 1:
            event = self.get_event()
            if event[0] == 'hook_down':
                self.status = self.standby
                break
        # TODO: terminate playing

    def playBusy(self):
        # TODO: play busy tone
        while 1:
            event = self.get_event()
            if event[0] == 'hook_down':
                self.status = self.standby
                break
        # TODO: terminate playing

    def silence(self):
        while 1:
            event = self.get_event()
            if event[0] == 'hook_down':
                self.status = self.standby
                break

    def inCall(self):
        while 1:
            event = self.get_event()
            if event[0] == 'hook_down':
                self.linphone.hangup()
                self.status = self.standby
                break
            if event[0] == 'disconnected':
                self.status = self.silence
                break
            if event[0] == 'dialed':
                self.linphone.sendDTMF(event[1])

pm = PhoneMachine()
