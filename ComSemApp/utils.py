import ssl
import nltk
import speech_recognition as sr
from django.http import HttpResponse, HttpResponseRedirect


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
        #gets the files
        file = request.FILES['audioBlob']
        
        #writes to an ogg file (ogg is an audio file format)
        with open("./in_file.ogg", "wb") as in_file:
            in_file.write(file.read())

        #pydub is needed to change an ogg file to a wav file
        from pydub import AudioSegment
        audio = AudioSegment.from_file("./in_file.ogg", format="ogg")
        file_handle = audio.export("./out_file.wav", format="wav")

        # Call STT
        #r is an object of an import "speech_recognition" declared at the top
        r = sr.Recognizer()


        #create a .wav file
        #transribe the wav file
        #IMPORTANT!!! THIS CAN ONLY TRANSCRIBE .wav files
        audio_file = "out_file.wav"
        with sr.AudioFile(audio_file) as source:
            audio = r.listen(source)
            try:
                print('converting audio to text...')
                text = r.recognize_google(audio)
                print(text)
                #capitalize sentence and add a period at the end of a expression
                return HttpResponse(text.capitalize() + ".")
            except Exception:
                print("======================ERROR======================")
                return HttpResponse("")