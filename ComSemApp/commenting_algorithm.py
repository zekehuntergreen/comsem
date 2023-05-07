def missing_words(expression, correct_expression) -> list[str] :
    """
    A function that returns words that are present in correct expression, but not in expression as a list of strings.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        missing_words (list): A list of strings, each string is a word that is not present in expression

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

def added_words(expression, correct_expression) -> list[str] :
    """
    A function that returns words that are present in expression, but not in correct expression as a list of strings.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        added_words (list): A list of strings, each string is a word that should not be in expression
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

def number_of_words(expression, correct_expression) -> list[str] :
    """
    A function that deals with words that are present in both the correct expression and the reformualtion, but are
    too great or too little in amount. It returns these words as two lists of strings
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        extra_present_words (list): A list of strings that stores the words that are too great in amount.
        missing_present_words (list): A list of strings that stores the words that are too little in amount.
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    extra_present_words = []
    missing_present_words = []

    present_words = [] # A list of strings that will hold the words that have been recorded
    number_present = [] # A list that will record the number of each word that is not present in the student submission
    correct_present_words = [] # A list of strings that will hold the words that have been recorded
    correct_number_present = [] # A list that will record the number of each word that is not present in the student submission

    # Get the words in the correct expression and their counts 
    for word in correct_expression_list:
        if word not in present_words:
            correct_present_words.append(word)
            correct_number_present.append(1)
        else:
            temp = present_words.index(word)
            correct_number_present[temp] += 1

    # Words in the inccorect expression
    for word in expression_list:
        if word not in present_words:
            present_words.append(word)
            number_present.append(1)
        else:
            temp = present_words.index(word)
            number_present[temp] += 1

    # Compares the present words in each expression to determine if there are extra or less of a given word
    for word in correct_expression_list:
        if word in expression_list:
            temp_correct = correct_present_words.index(word)
            temp =  present_words.index(word)
            if correct_number_present[temp_correct] > number_present[temp]:
                missing_present_words.append(word)
            elif number_present[temp] > correct_number_present[temp_correct]:
                extra_present_words.append(word)


    return extra_present_words, missing_present_words


def wrong_position(expression, correct_expression) -> list[str] :
    """
    A function that returns a list, of strings, of words that are in expression, but not in the same positon as 
    correct_expression.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        words_in_wrong_position (list): A list of strings that stores words in the wrong position in expression
    """
    lower_expression = expression.lower()
    expression_list = lower_expression.split()
    lower_correct_expression = correct_expression.lower()
    correct_expression_list = lower_correct_expression.split()
    words_in_wrong_position = []
    correct_expression_length = len(correct_expression_list)
    expression_length = len(expression_list)

    if(expression_length > correct_expression_length):
        min_length = correct_expression_length
    else:
        min_length = expression_length

    for x in range(min_length):
        if expression_list[x] != correct_expression_list[x] and expression_list[x] in correct_expression_list:
            words_in_wrong_position.append(expression_list[x])

    return words_in_wrong_position
            


def get_comments(expression, correct_expression) -> list[dict] :
    """
    This function utlizes the other functions in this file to find errors and provide feedback on those errors for students to 
    improve. This funciton is used in the review page to get the higlighsts and comments on student work.
    Args:
        expression (string): The student provided version of the expression, the reformulation.
        correct_expression (string): The correct expression the given expression will be compared to.
    
    Returns:
        comments (list): A list of dictionaries the indexs of errors made in the sentence and comments to identify them.
    """
    comments = []
    lower_expression = expression.lower()

    extra, lacking = number_of_words(expression, correct_expression)
    added = added_words(expression, correct_expression)
    missing = missing_words(expression, correct_expression)
    position = wrong_position(expression, correct_expression)

    i = 0
    word = ""
    start_index = 0
    while i != len(lower_expression):
        if lower_expression[i] == " ":
            end_index = i-1
            if word in position and word in extra:
                comments.append({'start':start_index,'end':end_index,'comment':"There is extra of this word and one or more of it is in the wrong postion."})
            elif word in position and word in lacking:
                comments.append({'start':start_index,'end':end_index,'comment':"There is too little of this word and one or more of it is in the wrong postion."})
            elif word in position:
                comments.append({'start':start_index,'end':end_index,'comment':"This word is in the wrong postion."})
            elif word in added:
                comments.append({'start':start_index,'end':end_index,'comment':"This word is not orginally part of the expression."})
            elif word in lacking:
                comments.append({'start':start_index,'end':end_index,'comment':"There is too little of the this word in your reformulation."})
            word = ""
            i +=1
            start_index = i
        else:
            word = word + lower_expression[i]
            i +=1

    # For the last word in the expression
    end_index = i-1
    if word in position and word in extra:
        comments.append({'start':start_index,'end':end_index,'comment':"There is extra of this word and one or more of it is in the wrong postion."})
    elif word in position and word in lacking:
        comments.append({'start':start_index,'end':end_index,'comment':"There is too little of this word and one or more of it is in the wrong postion."})
    elif word in position:
        comments.append({'start':start_index,'end':end_index,'comment':"This word is in the wrong postion."})
    elif word in added:
        comments.append({'start':start_index,'end':end_index,'comment':"This word is not orginally part of the expression."})
    elif word in lacking:
        comments.append({'start':start_index,'end':end_index,'comment':"There is too little of the this word in your reformulation."})

    left_over_words = ""
    for left_over_word in missing:
        if (left_over_words == ""): 
            left_over_words = left_over_words + " " + left_over_word
        else:
            left_over_words = left_over_words + ", " + left_over_word
            
    if len(missing) != 0:
        comments.append({'start':len(expression),'end':len(expression)+1,'comment':"You are missing these words:" + left_over_words + "."})
    return comments

if __name__ == "__main__":
    correct_expression = "Hello My Name is Elder Price"
    expression = "Hello My My Elder named Price elder"
    print("Correct Expression: " + correct_expression)
    print("Student Reformulation: " + expression)

    comments = get_comments(expression, correct_expression)

    for x in range(len(comments)):
        print(comments[x])