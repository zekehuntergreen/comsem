
#will run all other functions within the file in order to grade the expression
def grade_expression(expression, c_exp) :
    """This function takes in the expression the student provided as well as the correct expression 
    it then uses the functions in this file to grade their answer
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns: 
        grade: Placeholder, eventually will be overall grade
    """

    # get total percewntage of score
    #for example word presence 40% and word order 60%
    #work out scoring add them together at the end.
    #determine the deterimental values of extra words.
    grade = 10

    #this checks if the expression has no errors and if it does returns full credit
    if correct_expression(expression, c_exp) == True:
        return grade

    prescence_error = word_prescence(expression, c_exp)
    #check the word count of both strings using split to get the word amount

    #if the correct expression is longer
    #if len(c_exp.split()) > len(expression.split()):
    #    extra_words(expression, c_exp)

    #if they are the same length or expression is longer
    if len(c_exp.split()) <= len(expression.split()):
        word_order(expression, c_exp)


    return grade

def correct_expression(expression, c_exp):
    """This is a simple function that determines if the expressions are the
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
    """This is a function that determines if the desired words are present within the sentence
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        error_count(int): the amount of times that a word is not present
        location_of_error(list): a list of integers with the integer location of the desired words in the correct expression
    """
    c_exp_list = c_exp.split()
    expression_list = expression.split()
    error_count = 0

    #Very simpole checks if all correct words are present
    for x in range(len(c_exp_list)):
        if c_exp_list[x] not in expression:
            error_count+=1

    #So this next on checks if there are incorrect words, wondering if we want to grade with this as well 

    #for w in range(len(expression_list)):
    #    if expression_list[w] not in c_expression:
    #        error_count+=1
    return error_count

def word_order(expression, c_exp):
    """This is a function that determines if there is an error with the order of words
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        error_count: the amount of times that a word order error occurs
    """
    expression_list = expression.split()
    c_exp_list = c_exp.split()
    error_count = 0
    tested_positive = False
    test_next = False # checked in the previous loop that is was the word after previous in the original expression
    prev_wrong = False

    for x in range(len(expression_list)):
        #First checks if the word is the same in each expression in that position
        if x < len(c_exp_list):
            if expression_list[x] == c_exp_list[x]:
                tested_positive = True

        #This series of ifs 
        if (x + 1) < len(expression_list): # makes sure that it will not go out of index checking the next word
            if expression_list[x] in c_exp_list: #checks if the word is in the correct expression
                word_index = c_exp_list.index(expression_list[x]) #sets word index equal to the index of the word in the orignal expression
                if (word_index + 1) < len(c_exp_list): #make sure that there is a word after the desired word
                    if expression_list[x+1] == c_exp_list: #checks if that word matches the next word in the expression
                        tested_positive = True
                        test_next = True
                else:
                    tested_positive = False

        #if a word that is not present in the original list adds an error
        if expression_list[x] not in c_exp_list:
            tested_positive = True
            error_count += 1
        
        if tested_positive != True and test_next == False:
            error_count += 1
            prev_wrong = True


        if tested_positive != True and test_next == True:
            test_next = False



    #for x in range(len(expression_list)):
    #things that need to be done:
    #check that all words are presecheck whichever has more words
    #if expresssion has more words, use extra words if not use missing words
    #Use split then take the len from the list and determine.
    #check all words and what comes after to determine if poitns given, for example:
    #if the sentence is "My Father is a carpenter"
    # and the student says "My older Father is a carpenter" this should still be around 90%

    #Way to do this, have two if statements and check to see if the next word is the end of the sentence,
    #USe the if statements to first check if the lcoations match,
    #If they do not match, use the second statemnet to check if the current word exists in the original expression
    #If it exists then check the word after, if the after words are equal give credit.

    return error_count


expression = "Hello my name pineapple Elder Price"
print(expression)
c_expression = "Hello my name is Elder Price"
grade = 0

#FOUND AN ISSUE IMPORTANT TO BRING UP WHAT IF THEY GIVE AN ENTIRELY CORRECT ORDER 
#BUT ARE MISSING A WORD I WOULD GIVE FULL CREDIT IN THIS CASE
#EXAMPLE:
#"Hello my name elder price"
#"Hello my name is elder price"
#I beleive full credit for order because the words all go together except one but I can be swayed to take off a point depedning
#Will code in correction and comment it out
print(correct_expression(expression, c_expression))
print("Presence error count:", word_prescence(expression, c_expression))
print("Word order error count:", word_order(expression, c_expression))