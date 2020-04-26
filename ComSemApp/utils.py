import nltk
from nltk.data import load
import tensorflow

def pos_tag(expression):
    from ComSemApp.models import Tag, Word, SequentialWords
    nltk.data.path.append("/nltk_data");
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

    expression_text = expression.expression.lower()
    tokens = nltk.word_tokenize(expression_text)
    tagged = nltk.pos_tag(tokens)


    word_position = 0
    for word, tag in tagged:
        # tags
        dictionary_tag, created = Tag.objects.get_or_create(tag=tag)
        # words
        dictionary_word, created = Word.objects.get_or_create(form=word, tag=dictionary_tag)
        # sequential words
        SequentialWords.objects.create(
            expression = expression,
            word = dictionary_word,
            position = word_position,
        )
        word_position += 1
