import json
import requests

#constants
API_URL = "https://f8nay4b9u5.execute-api.us-west-2.amazonaws.com/test/predictgrammar"


class BERTModel():
    def __init__(self) -> None:
        self.worksheet_batch = {}

    def generateHints(self, expression_lst, worksheet_id):
        working_expression_list = []
        for expression_obj in expression_lst:
            working_expression_list.append(expression_obj.expression)
        self.worksheet_batch['data'] = working_expression_list #store expression list at key that matches worksheet_id
        #QUESTION: Do we wait until the dictionary gets full enough to send batch or should it send about right away?
        #if need to wait do that, if not, don't
        json_object = json.dumps(self.worksheet_batch, indent=4)
        response = requests.post(API_URL, data=json_object)

        decoded_results = response.content.decode('utf-8').strip("\"")
        results_list = list(decoded_results)
        #SEND JSON
        #Need return to specify 1. Worksheet ID and expression ID 2. Error type(s) 3. score for each error type
        
        #convert predictions back to dictionary (probably new function)
        #use predictions to write and add hints to expessions
        #for exp_obj in expr_list 
        #prune results, get rid of anything less than certain threshold, examine remaining data to create hints
        #assign hint to appropriate expression_obj, save, no return (maybe return true to say completed)

        for index in range(len(expression_lst)):
            expression_obj = expression_lst[index]
            hint, tag = self.convert_to_hints((int(results_list[index])))
            expression_obj.hint = hint
            expression_obj.error_tag = tag
            expression_obj.save()
            
    def convert_to_hints(self, result):
        if result == 0:
            return "Make sure the verb agrees with its subject", 'SV agr'
        else:
            return "No error was found", 'NP'