from ComSemApp.BERT.wait_queue import WaitQueue
from ComSemApp.BERT.wait_queue import WaitQueue

class BERTModel():
    def __init__(self) -> None:
        self.in_queue = WaitQueue()
        #out_queue = WaitQueue()

    def giveHint(self):
        input = self.in_queue.get_item()
        #do something with input
        #"generate" hint
        hint = "This is a hint"
        return hint
