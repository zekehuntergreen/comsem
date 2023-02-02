def grade_expression(expression, c_exp) :
    """
    This function takes in the expression the student provided as well as the correct expression 
    it then uses the functions in this file to grade their answer
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns: 
        grade (float): Placeholder, eventually will be overall grade
    """

    #this checks if the expression has no errors and if it does returns full credit
    if correct_expression(expression, c_exp) == True:
        return 100

    expression_list = expression.split()
    c_exp_list = c_exp.split()

    total_order_score = 0
    total_word_count = len(c_exp_list)
    position_error_count = word_position(expression, c_exp)
    position_percent = ((total_word_count - position_error_count) / total_word_count) * 100
    position_percent_of_order_score= position_percent * .2

    total_order_score = total_order_score + position_percent_of_order_score
    if word_count(expression, c_exp) == True:
        total_order_score = total_order_score + 10
    print(total_order_score)

    order_error_count = word_order(expression, c_exp)
    order_percent = ((total_word_count - order_error_count) / total_word_count) * 100
    print(order_percent)
    order_percent_of_total = order_percent * .7
    total_order_score = total_order_score + order_percent_of_total

    print(total_order_score)

    presence_error_count = word_prescence(expression, c_exp)
    presence_percent = ((total_word_count - presence_error_count) / total_word_count) 
    presence_score = presence_percent * 100

    print(presence_score)
    grade = 0 
    grade = (total_order_score * .5) + (presence_score * .5)
    print(grade)

    return grade

def correct_expression(expression, c_exp):
    """
    This is a simple function that determines if the expressions are the
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        bool: simple true/false return for if the expression is correct
    """
    if expression == c_exp:
        return True
    return False

def word_prescence(expression, c_exp):
    """
    This is a function that determines if the desired words are present within the sentence
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        error_count(int): the amount of times that a word is not present
    """
    c_exp_list = c_exp.split()
    expression_list = expression.split()
    error_count = 0

    #Very simple checks if all correct words are present
    for x in range(len(c_exp_list)):
        if c_exp_list[x] not in expression:
            error_count+=1

    return error_count

def word_order(expression, c_exp):
    """
    This is a function that determines if there is an error with the order of words
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        error_count (int): the amount of times that a word order error occurs
    """
    expression_list = expression.split()
    c_exp_list = c_exp.split()
    error_count = 0
    for x in range(len(expression_list)):
        if (x + 1) < len(expression_list): # makes sure that it will not go out of index checking the next word
            if expression_list[x] in c_exp_list: #checks if the word is in the correct expression
                word_index = c_exp_list.index(expression_list[x]) #sets word index equal to the index of the word in the orignal expression
                if (word_index + 1) < len(c_exp_list): #make sure that there is a word after the desired word
                    if expression_list[x+1] == c_exp_list[word_index+1]: #checks if that word matches the next word in the expression
                        continue
                    else:
                        error_count += 1

        if x == len(expression_list)-1: # if the index is to the last word in expression, since the last word has no word after it
            word_index = c_exp_list.index(expression_list[x]) # gets the index of the word in the correct expression
            if word_index == len(c_exp_list)-1: # checks if the word is the last word in the correct expression
                continue
            else:
                error_count += 1

    return error_count

def word_position(expression, c_exp):
    """
    This is a function that determines if there is an error with word positions, will be worth 10% or 20%
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        error_count (int): the amount of times that a word order error occurs
    """
    expression_list = expression.split()
    c_exp_list = c_exp.split()
    error_count = 0
    # checks if the postiion of a word is the same in each expression
    for x in range(len(expression_list)):
        if x < len(c_exp_list):
            if expression_list[x] != c_exp_list[x]:
                error_count += 1

    return error_count

def word_count(expression, c_exp):
    """
    This is a function that determines if the number of words in the expressions are the same, will be worth 10%
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        check (bool): True if the amount of words in the sentnece are equal, false otherwise
    """
    expression_list = expression.split()
    c_exp_list = c_exp.split()
    check = False
    if len(expression_list) == len(c_exp_list):
        check = True
    return check

expression = "Hello my name pineapple Elder Price"
print(expression)
c_exp = "Hello my name is Elder Price"
print(correct_expression(expression, c_exp))
print("Presence error count:", word_prescence(expression, c_exp))
print("Word order error count:", word_order(expression, c_exp))

expression_list = expression.split()
c_exp_list = c_exp.split()

total_order_score = 0
total_word_count = len(c_exp_list)
position_error_count = word_position(expression, c_exp)
position_percent = ((total_word_count - position_error_count) / total_word_count) * 100
position_percent_of_order_score= position_percent * .2

total_order_score = total_order_score + position_percent_of_order_score
if word_count(expression, c_exp) == True:
    total_order_score = total_order_score + 10

order_error_count = word_order(expression, c_exp)
order_percent = ((total_word_count - order_error_count) / total_word_count) * 100
order_percent_of_total = order_percent * .7
total_order_score = total_order_score + order_percent_of_total

print(total_order_score)

presence_error_count = word_prescence(expression, c_exp)
presence_percent = ((total_word_count - presence_error_count) / total_word_count) 
presence_score = presence_percent * 100

print(presence_score)
grade = 0 
grade = (total_order_score * .5) + (presence_score * .5)
print(grade)