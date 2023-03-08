def grade_reformulation(expression, c_exp) :
    """
    This function takes in the reformulation the student provided as well as the correct expression 
    it then uses the functions in this file to grade their answer
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns: 
        grade (float): Placeholder, eventually will be overall grade
    """

    #SELF NOTE, NO ISSUES WITH USING WORD COUNT FOR PERCENTAGES
    #CAHNGE THEM ALL TO LOWERS

    # This checks if the expression has no errors and if it does returns full credit
    if expression == c_exp:
        return 100

    #Create a case for when the expression has nothing

    c_exp_list = c_exp.split()
    # Begins with checking the position of words
    total_order_score = 0
    total_word_count = len(c_exp_list)
    position_error_count = word_position(expression, c_exp)

    # Math for the algorithm, converts it to a percentage and then converts it to 20% of the overall grade
    position_percent = ((total_word_count - position_error_count) / total_word_count) * 100
    position_percent_of_order_score = position_percent * .25
    print("Position Percentage: ", position_percent)
    # Adds to total
    total_order_score = total_order_score + position_percent_of_order_score

    # Performs the word order check
    order_error_count = word_order(expression, c_exp)
    # Once again converts to percent, but this section is instead worth 70% of the order portion
    order_percent = ((total_word_count - order_error_count) / total_word_count) * 100
    print("Order percentage: ", order_percent)
    order_percent_of_total = order_percent * .75
    total_order_score = total_order_score + order_percent_of_total

    # The presence check
    presence_error_count = word_prescence(expression, c_exp)
    # Converts presence score to a percent which is the overrall score for the presence portion
    presence_percent = ((total_word_count - presence_error_count) / total_word_count) * 100
    presence_score = presence_percent * .7
    print("Presence Score: ", presence_percent)

    # Sentence length check
    length_percent = word_count(expression, c_exp)
    length_score = length_percent *.2
    presence_score = presence_score + length_score
    print("Sentence Length Score: ", length_percent)

    # Extra Words check
    extra_percent = extra_words(expression, c_exp)
    extra_score = extra_percent * .1
    presence_score = presence_score + extra_score
    print("Extra Words Score: ", extra_percent)
    

    # Combines the two sections, both being weighted at 50%
    grade = (total_order_score * .5) + (presence_score * .5)
    return grade

#change presence to include mutiple instances of words, not jsut one instance
def word_prescence(expression, c_exp):
    """
    This is a function that determines if the words from the correct expression are present within the reformulation
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        error_count(int): the amount of times that a word is not present
    """
    l_expression = expression.lower()
    expression_list = l_expression.split()
    l_c_exp = c_exp.lower()
    c_exp_list = l_c_exp.split()
    error_count = 0

    present_words = [] # A list of strings that will hold the words that have been recorded
    number_present = [] # A list that will record the number of each word that is not present in the student submission
    for x in c_exp_list:
        if x not in present_words: # Checks if the word is already present in list
            #If word is not present, the word is appened to the list and the number list has one appeneded
            present_words.append(x) 
            number_present.append(1)
        else:
            #if the word is already in the previous list, the value at the index of the word is increased in the numbers list
            temp = present_words.index(x)
            number_present[temp] += 1

    # This counts the words in the student submission and alters number_present based off them
    for y in expression_list:
        if y in present_words: # Checks if the word is present in the correct expression
            temp = present_words.index(y)
            if(number_present[temp] == 0): # A case that oocurs when there is an excess number of the given word in the student expression
                error_count += 1
            else:
                #When a word is present, 1 is deleted from the word's index in number_present
                number_present[temp] -= 1
    
    # Counts the errors based on what is left in number_present
    for c in range(len(number_present)):
        if(number_present[c] != 0):
            error_count += number_present[c]

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
    l_expression = expression.lower()
    expression_list = l_expression.split()
    l_c_exp = c_exp.lower()
    c_exp_list = l_c_exp.split()

    # If none of the words are present order must be zero as well
    if(word_prescence(expression, c_exp) == len(l_c_exp)):
        return len(l_c_exp)
    
    error_count = 0
    for x in range(len(expression_list)):
        if (x + 1) < len(expression_list): # Makes sure that it will not go out of index checking the next word
            if expression_list[x] in c_exp_list: # Checks if the word is in the correct expression
                word_index = c_exp_list.index(expression_list[x]) # Sets word index equal to the index of the word in the orignal expression
                if (word_index + 1) < len(c_exp_list): # Make sure that there is a word after the desired word
                    if expression_list[x+1] == c_exp_list[word_index+1]: # Checks if that word matches the next word in the expression
                        continue
                    else:
                        error_count += 1

        if x == len(expression_list)-1: # If the index is to the last word in expression, since the last word has no word after it
            if expression_list[x] in c_exp_list: # Checks if the word is in the correct expression
                word_index = c_exp_list.index(expression_list[x]) # Gets the index of the word in the correct expression
                if word_index == len(c_exp_list)-1: # Checks if the word is the last word in the correct expression
                    continue
                else:
                    error_count += 1

    return error_count

def word_position(expression, c_exp):
    """
    This is a function that determines if there is an error with word positions
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        error_count (int): the amount of times that a word order error occurs
    """
    l_expression = expression.lower()
    expression_list = l_expression.split()
    l_c_exp = c_exp.lower()
    c_exp_list = l_c_exp.split()
    error_count = 0
    # Checks if the postiion of a word is the same in each expression
    for x in range(len(expression_list)):
        if x < len(c_exp_list):
            if expression_list[x] != c_exp_list[x]:
                error_count += 1

    return error_count


def word_count(expression, c_exp):
    """
    This is a function that determines if the number of words in the expressions are the same
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        correct_percent(int): The percentage the student got in this given section
    """
    l_expression = expression.lower()
    expression_list = l_expression.split()
    l_c_exp = c_exp.lower()
    c_exp_list = l_c_exp.split()
    error_count = 0
    expression_len = len(expression_list)
    c_exp_len = len(c_exp_list)
    if expression_len == c_exp_len:
        return 100
    
    if expression_len > c_exp_len:
        error_count = expression_len - c_exp_len
    else:
        error_count = c_exp_len - expression_len

    half_len = c_exp_len/2
    correct_percent = 0
    if error_count <= half_len:
        correct_percent = (c_exp_len - error_count)/c_exp_len
        correct_percent = correct_percent * 100
        return correct_percent
    else:
        return correct_percent
    
def extra_words(expression, c_exp):
    """
    This is a function that determines if the student added extra words within their reformulation
    Args:
        expression (string): The student provided version of the expression
        c_exp (string): The correct expression to be comapred to
    
    Returns:
        correct_percent(int): The percentage the student got in this given sectione
    """
    l_expression = expression.lower()
    expression_list = l_expression.split()
    l_c_exp = c_exp.lower()
    c_exp_list = l_c_exp.split()
    error_count = 0

    for x in expression_list:
        if x in c_exp_list:
            continue
        else:
            error_count += 1

    half_len = len(c_exp_list)/2
    correct_percent = 0
    if error_count <= half_len:
        correct_percent = (len(c_exp_list) - error_count)/len(c_exp_list)
        correct_percent = correct_percent * 100
        return correct_percent
    else:
        return correct_percent

c_exp = "Hello My Name is Elder Price."
expression = "Hello My Pineapple is Elder Price."
print(expression)
print(c_exp)
print("Your overall grade was:", grade_reformulation(expression, c_exp))
