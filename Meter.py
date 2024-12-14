import random
import threading
import time

class Meter:
    def __init__(self):
        self.__input = None
        self.__output = None
        self.net= 0

    def measure(self, duration):
        start_time =  time.time()
        def produce_energy():
            while time.time() - start_time < duration:
                self.__output = random.randint(30, 60)
                self.__input = random.randint(30, 40)
                self.net = self.__output - self.__input
                time.sleep(1)

        energy_thread = threading.Thread(target=produce_energy())
        energy_thread.start()
        energy_thread.join(timeout=duration)

        return self.net
