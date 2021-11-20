from queue import Queue

class WaitQueue():
    def __init__(self) -> None:
        self.queue = Queue()
        #ready = False

    def add_item(self, param_item):
        self.queue.put(param_item)

    def get_item(self):
        #if(self.ready):
            return self.queue.get()
        #else:
            #wait
            #pass