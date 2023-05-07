def missing_words(expression, correct_expression) -> list[str] :
    """
    A function that returns words that are present in correct expression, but not in expression as a list of strings.
    Args:
        expression (list): A list version of the student provided version of the expression, the reformulation.
        correct_expression (list): A list version of the correct expression the given expression will be compared to.
    
    Returns:
        missing_words (list): A list of strings, each string is a word that is not present in expression

    """
    missing_words = []

    for word in correct_expression:
        if word not in expression:
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
    added_words = []

    for word in expression:
        if word in correct_expression:
            continue
        else:
            added_words.append(word)
    
    return added_words

def number_of_words(expression, correct_expression) -> list[str] :
    """
    A function that deals with words that are present in both the correct expression and the reformualtion, but are
    too great or too little in amount. It returns these words as two lists of strings
    Args:
        expression (list): A list version of the student provided version of the expression, the reformulation.
        correct_expression (list): A list version of the correct expression the given expression will be compared to.
    
    Returns:
        extra_present_words (list): A list of strings that stores the words that are too great in amount.
        missing_present_words (list): A list of strings that stores the words that are too little in amount.
    """
    extra_present_words = []
    missing_present_words = []

    present_words = [] # A list of strings that will hold the words that have been recorded
    number_present = [] # A list that will record the number of each word that is is present in the student submission
    correct_present_words = [] # A list of strings that will hold the words that have been recorded, in the correct expression
    correct_number_present = [] # A list that will record the number of each word that is preset in the correct expression

    # Get the words in the correct expression and their counts 
    for word in correct_expression:
        if word not in present_words:
            correct_present_words.append(word)
            correct_number_present.append(1)
        else:
            temp = present_words.index(word)
            correct_number_present[temp] += 1

    # Words in the inccorect expression
    for word in expression:
        if word not in present_words:
            present_words.append(word)
            number_present.append(1)
        else:
            temp = present_words.index(word)
            number_present[temp] += 1

    # Compares the present words in each expression to determine if there are extra or less of a given word
    for word in correct_expression:
        if word in expression:
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
        expression (list): A list version of the student provided version of the expression, the reformulation.
        correct_expression (list): A list version of the correct expression the given expression will be compared to.
    
    Returns:
        words_in_wrong_position (list): A list of strings that stores words in the wrong position in expression
    """
    words_in_wrong_position = []
    correct_expression_length = len(correct_expression)
    expression_length = len(expression)

    if(expression_length > correct_expression_length):
        min_length = correct_expression_length
    else:
        min_length = expression_length

    for x in range(min_length):
        if expression[x] != correct_expression[x] and expression[x] in correct_expression:
            words_in_wrong_position.append(expression[x])

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
    lower_correct_expression = correct_expression.lower()
    expression_list = lower_expression.split()
    correct_expression_list = lower_correct_expression.split()


    extra, lacking = number_of_words(expression_list, correct_expression_list)
    added = added_words(expression_list, correct_expression_list)
    missing = missing_words(expression_list, correct_expression_list)
    position = wrong_position(expression_list, correct_expression_list)

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