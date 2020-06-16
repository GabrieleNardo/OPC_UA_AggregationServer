import time
import threading

class PollingService(threading.Thread):
    def __init__(self, nodeid , ref_int , client):
        threading.Thread.__init__(self)      
        self._stopper = threading.Event()  #used ih thread stopping
        self.ref_int = ref_int
        self.nodeid = nodeid
        self.client = client
    
    def stop(self): 
        self._stopper.set()
    
    def stopped(self): 
        return self._stopper.isSet()

    def run(self):
        while not(self.stopped()):
            self.client.readData(self.nodeid)
            time.sleep(self.ref_int)