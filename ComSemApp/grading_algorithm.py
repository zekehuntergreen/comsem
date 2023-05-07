def grade_reformulation(reformulation, correct_expression) -> float :
    """
    This function takes in the reformulation the student provided as well as the correct expression 
    it then uses the functions in this file to grade their answer
    Args:
        reformulation (string): The student provided version of the expression.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns: 
        overall_grade (float): The final grade based upon the scores recieved and the
        weights applied to each section.
    """

    # This checks if the expression has no errors and if it does returns full credit
    if reformulation.lower() == correct_expression.lower():
        return 100
    # Initialize the total scores
    total_order_score = 0
    total_presence_score = 0
    
    # Declarations of algorithm percentages
    # Order Conversions
    order_weight = .5 # 50% of total grade
    position_conversion = .25 # 25% of total order score
    order_conversion = .75 # 75% of total order score
    # Presence Conversions
    presence_weight = .5 # 50% of total grade
    presence_conversion = .6 # 70% of total presence score
    legnth_converison = .2 # 20% of total presence score
    extra_converison = .2 # 10% of total presence score

    # The Postion check
    position_grade = word_position(reformulation, correct_expression)
    position_percent = position_grade * position_conversion
    # Adds to total order score
    total_order_score += position_percent

    # The Presence check
    presence_grade = word_prescence(reformulation, correct_expression)
    presence_percent = presence_grade * presence_conversion
    # Adds to total presence score
    total_presence_score += presence_percent

    # The Word Order check
    order_grade = word_order(reformulation, correct_expression, presence_grade)
    order_percent = order_grade * order_conversion
    # Adds to total order score
    total_order_score += order_percent

    # The Sentence Length check
    length_grade = expression_length(reformulation, correct_expression)
    length_percent = length_grade * legnth_converison
    # Adds to total presence score
    total_presence_score += length_percent

    # The Extra Words check
    extra_grade = extra_words(reformulation, correct_expression)
    extra_percent = extra_grade * extra_converison
    # Adds to total presence score
    total_presence_score += extra_percent
    
    # Combines the two sections
    overall_grade = (total_order_score * order_weight) + (total_presence_score * presence_weight)
    return overall_grade

def word_prescence(expression, correct_expression) -> float :
    """
    This is a function that determines if the words from the given correct expression 
    are present within the given expression. It then calculates a percentage score 
    based upon the length of the given correct expresssion and errors, then returns it.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        percentage (float): The amount of errors compared to the length of the correct expression.
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    correct_expression_length = len(correct_expression_list)
    error_count = 0

    present_words = [] # A list of strings that will hold the words that have been recorded
    number_present = [] # A list that will record the number of each word that is not present in the student submission
    for word in correct_expression_list:
        if word not in present_words:
            #If word is not present, the word is appened to the list and the number list has one appeneded
            present_words.append(word) 
            number_present.append(1)
        else:
            #if the word is already in the previous list, the value at the index of the word is increased in the numbers list
            temp = present_words.index(word)
            number_present[temp] += 1

    # This counts the words in the student submission and alters number_present based off them
    for word in expression_list:
        if word in present_words:
            temp = present_words.index(word)
            # A case that oocurs when there is an excess number of the given word in the student expression
            if(number_present[temp] == 0):
                error_count += 1           
            else:
                # When a word is present, 1 is deleted from the word's index in number_present
                number_present[temp] -= 1
    
    # Counts the errors based on what is left in number_present
    for x in range(len(number_present)):
        if(number_present[x] != 0):
            error_count += number_present[x]

    percentage = 0
    # Simple check to make sure that if there are too many duplicates 0 is returned
    if(error_count < correct_expression_length):
        percentage = ((correct_expression_length - error_count) / correct_expression_length) * 100
    return percentage

def word_order(expression, correct_expression, presence_grade) -> float :
    """
    This is a function that determines if there is an error with the order of words in the given
    expression based upon the order of words in the given correct expression. It then calculates 
    a percentage score based upon the length of the given correct expresssion 
    and errors, then returns it.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
        presence_grade (int): The grade received on presence.
    
    Returns:
        percentage (float): The amount of errors compared to the length of the correct expression.
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    correct_expression_length = len(expression_list)

    # If none of the words are present order must be zero as well
    if(presence_grade == 0):
        return 0
    
    error_count = 0
    for x in range(len(expression_list) - 1):
            if expression_list[x] in correct_expression_list: 
                word_index = correct_expression_list.index(expression_list[x])
                # Checks if that word matches the next word in the expression and Makes sure that it is not the last word in the expression
                if (word_index + 1) < len(correct_expression_list) and expression_list[x + 1] == correct_expression_list[word_index + 1]: 
                    continue
                else:
                    error_count += 1

    x = len(expression_list) - 1
    if expression_list[x] in correct_expression_list:
        word_index = correct_expression_list.index(expression_list[x])
        # Checks if the word is the last word in the correct expression
        if word_index != len(correct_expression_list) - 1:
            error_count += 1


    percentage = ((correct_expression_length - error_count) / correct_expression_length) * 100
    return percentage

def word_position(expression, correct_expression) -> float :
    """
    This is a function that determines if there is an error with word positions in the given
    expression, compared to the given correct expression. The function then calculates 
    a percentage score based upon the length of the given correct expresssion 
    and errors, then returns it.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        percentage (float): The amount of errors compared to the length of the correct expression
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    correct_expression_length = len(correct_expression_list)
    error_count = 0
    # Checks if the postiion of a word is the same in each expression
    for x in range(len(expression_list)):
        if x < correct_expression_length:
            if expression_list[x] != correct_expression_list[x]:
                error_count += 1
        else:
            error_count += 1
    
    if error_count > correct_expression_length:
        error_count = correct_expression_length

    percentage = ((correct_expression_length - error_count) / correct_expression_length) * 100
    return percentage


def expression_length(expression, correct_expression) -> float :
    """
    This is a function that determines if the number of words in the given expression and
    given correct expression are the same. If they are not and the deffecernce is greater
    than half the length of the correct expression, 89the student recieves 0.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        percentage (float): The amount of errors compared to the length of the correct expression
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    error_count = 0
    expression_len = len(expression_list)
    correct_expression_len = len(correct_expression_list)

    if expression_len == correct_expression_len:
        return 100
    error_count = abs(expression_len - correct_expression_len)

    half_len = correct_expression_len / 2
    percentage = 0
    if error_count <= half_len:
        percentage = (correct_expression_len - error_count) / correct_expression_len
        percentage = percentage * 100
    return percentage
    
def extra_words(expression, correct_expression) -> float :
    """
    This is a function that determines if the student added extra words to their given expression
    by comparing to the given correct expression. Once again if they add more words than half
    the length of the correct expression they receive a 0.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression to be comapred to
    
    Returns:
        percentage (flaot): The amount of errors compared to the length of the correct expression
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    error_count = 0

    for word in expression_list:
        if word in correct_expression_list:
            continue
        else:
            error_count += 1

    half_len = len(correct_expression_list) / 2
    percentage = 0
    if error_count <= half_len:
        percentage = (len(correct_expression_list) - error_count) / len(correct_expression_list)
        percentage = percentage * 100
    return percentage
    
if __name__ == "__main__":
    correct_expression = "He walked the dog"
    expression = "She walked the dog"
    print(expression)
    print(correct_expression)
    print("Your overall grade was:", grade_reformulation(expression, correct_expression))
