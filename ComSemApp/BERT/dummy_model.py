import json
from ComSemApp.BERT.wait_queue import WaitQueue

class BERTModel():
    def __init__(self) -> None:
        self.worksheet_batch = {}

    def generateHints(self, expression_lst, worksheet_id):
        working_expression_list = []
        for expression_obj in expression_lst:
            working_expression_list.append(expression_obj.expression)
        self.worksheet_batch[worksheet_id] = working_expression_list #store expression list at key that matches worksheet_id
        #QUESTION: Do we wait until the dictionary gets full enough to send batch or should it send about right away?
        #if need to wait do that, if not, don't
        json_object = json.dumps(self.worksheet_batch, indent=4)
        # print(json_object)
        #SEND JSON
        #Need return to specify 1. Worksheet ID and expression ID 2. Error type(s) 3. score for each error type
        
        #convert predictions back to dictionary (probably new function)
        #use predictions to write and add hints to expessions
        #for exp_obj in expr_list 
        #prune results, get rid of anything less than certain threshold, examine remaining data to create hints
        #assign hint to appropriate expression_obj, save, no return (maybe return true to say completed)
        for expression_obj in expression_lst:
            expression_obj.hint = "This is a hint"
            expression_obj.save()