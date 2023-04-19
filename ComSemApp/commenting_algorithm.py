def missing_words(expression, correct_expression):
    """

    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        missing_words

    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    missing_words = []

    for word in correct_expression_list:
        if word not in expression_list:
            missing_words.append(word)

    return missing_words

def added_words(expression, correct_expression):
    """

    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        added_words
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    added_words = []

    for word in expression_list:
        if word in correct_expression_list:
            continue
        else:
            added_words.append(word)
    
    return added_words

def number_of_words_words(expression, correct_expression):
    """

    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        extra_present_words
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    extra_present_words = []
    missing_present_words = []

    present_words = [] # A list of strings that will hold the words that have been recorded
    number_present = [] # A list that will record the number of each word that is not present in the student submission

    # Get the words in the correct expression and their counts 
    for word in correct_expression_list:
        if word not in present_words:
            present_words.append(word)
            number_present.append(1)
        else:
            temp = present_words.index(word)
            number_present[temp] += 1

    # Determines if there are too many of a word
    for word in expression_list:
        if word in present_words and word not in extra_present_words:
            temp = present_words.index(word)
            if(number_present[temp] == 0):
                extra_present_words.append(word)
            else:
                number_present[temp] -= 1

    # Determines if there is too little of a word
    for word in expression_list:
        if word in present_words and word not in missing_present_words:
            temp = present_words.index(word)
            if(number_present[temp] != 0):
                missing_present_words.append(word)


    return extra_present_words, missing_present_words


def wrong_postion(expression, correct_expression):
    """

    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        words_in_wrong_position
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    words_in_wrong_position = []
    correct_expression_length = len(correct_expression_list)

    for x in range(correct_expression_length):
        if correct_expression_list[x] != expression_list[x]:
            words_in_wrong_position.append(correct_expression_list[x])

    return words_in_wrong_position
            


if __name__ == "__main__":
    correct_expression = "Hello."
    expression = "Hello."
    print(expression)
    print(correct_expression)