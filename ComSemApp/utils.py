import ssl
import nltk
import speech_recognition as sr
from django.http import HttpResponse, HttpResponseRedirect
import tempfile
import os
from pydub import AudioSegment

def pos_tag(expression):
    from ComSemApp.models import Tag, Word, SequentialWords
    nltk.data.path.append("/nltk_data")

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

    expression_text = expression.expression.lower()
    tokens = nltk.word_tokenize(expression_text)
    tagged = nltk.pos_tag(tokens)


    word_position = 0
    for word, tag in tagged:
        # tags
        dictionary_tag, _ = Tag.objects.get_or_create(tag=tag)
        #words
        dictionary_word, _ = Word.objects.get_or_create(form=word, tag=dictionary_tag)
        #sequential words
        SequentialWords.objects.create(
            expression = expression,
            word = dictionary_word,
            position = word_position,
        )
        word_position += 1


def transcribe(request):
    if request.method == 'POST': 
        # gets the files
        file = request.FILES['audioBlob']
        
        # tempfile.mkstemp returns a tuple containing an OS level handle
        # and absolute path of the temp file
        in_file_handle, temp_in_path = tempfile.mkstemp(suffix=".ogg")
        out_file_handle, temp_out_path = tempfile.mkstemp(suffix=".wav")
        with open(temp_in_path, 'wb') as temp_in:
            temp_in.write(file.read())
            
        # pydub is needed to change an ogg file to a wav file
        
        audio = AudioSegment.from_file(temp_in_path, format="ogg")
        audio.export(temp_out_path, format="wav")

        # Call STT
        # r is an object of an import "speech_recognition" declared at the top
        r = sr.Recognizer()

        # create a .wav file
        # transribe the wav file
        # IMPORTANT!!! THIS CAN ONLY TRANSCRIBE .wav files
        audio_file = temp_out_path
        with sr.AudioFile(audio_file) as source:
            audio = r.listen(source)
            
            try:
                print('converting audio to text...')
                text = r.recognize_google(audio)
                print(text)
                #closes the temp files
                os.close(in_file_handle)
                os.close(out_file_handle)
                # capitalize sentence and add a period at the end of a expression
                return HttpResponse(text.capitalize() + ".")
            
            except Exception:
                os.close(in_file_handle)
                os.close(out_file_handle)
                return HttpResponse("")
