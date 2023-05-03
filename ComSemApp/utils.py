import api_keys
import nltk
import ssl
import tempfile
import speech_recognition as sr
from django.http import HttpResponse
from django.core.files.uploadedfile import UploadedFile
import tempfile

from os import close
from pydub import AudioSegment
from requests import get, Response

from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseServerError, Http404, JsonResponse

def pos_tag(expression):
    from ComSemApp.models import Tag, Word, SequentialWords
    nltk.data.path.append("/nltk_data")

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    # nltk.download('punkt')
    # nltk.download('averaged_perceptron_tagger')

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
                text = r.recognize_google(audio)
                #closes the temp files
                close(in_file_handle)
                close(out_file_handle)
                # capitalize sentence
                return HttpResponse(text.capitalize())
            
            except Exception:
                close(in_file_handle)
                close(out_file_handle)
                return HttpResponse("")


def transcribe_and_get_length_audio_file(file : UploadedFile) -> tuple[str, int]:
    """
        Utilizes the Google audio transcription API to transcribe and get the length of an
        audio file of the Django UploadedFile class
        
        Arguments:
            file : UploadedFile -- The file to transcribe and get length of

        Returns:
            tuple(str, int) -- The transcription and length (in milliseconds) of the file
    """
    # tempfile.mkstemp returns a tuple containing an OS level handle
    # and absolute path of the temp file
    in_file_handle : int
    temp_in_path : bytes
    out_file_handle : int
    temp_out_path : bytes

    in_file_handle, temp_in_path = tempfile.mkstemp(suffix=".ogg")
    out_file_handle, temp_out_path = tempfile.mkstemp(suffix=".wav")
    with open(temp_in_path, 'wb') as temp_in:
        temp_in.write(file.read())
        
    # pydub is needed to change an ogg file to a wav file
    audio : AudioSegment = AudioSegment.from_file(temp_in_path, format="ogg")
    audio.export(temp_out_path, format="wav")
    length = len(audio)

    # r is an object of an import "speech_recognition" declared at the top
    r = sr.Recognizer()

    # sr.Recognizer can only take .wav files
    audio_file = temp_out_path
    with sr.AudioFile(audio_file) as source:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            #closes the temp files
            close(in_file_handle)
            close(out_file_handle)
            # capitalize sentence
            return (text, length)
        except Exception:
            close(in_file_handle)
            close(out_file_handle)
            return ("", length)
def get_youglish_videos(request : HttpRequest) -> HttpResponse:
    """
        Polls YouGlish REST API for YouTube video clips containing the phrase given in an HTTP GET request

        Arguments:
            request : HttpRequest - a Django HttpRequest object which should contain GET request data
                phrase (required) - The phrase to search for
                accent (optional) - A code which allows the client to search for a particular accent
                page   (optional) - Used for pagination to get more results
        
        Returns:
            HttpResponse - A Django HttpResponse object indicating the outcome of the request:
                JsonResponse           (200) - A success message containing the requested data in JSON format
                HttpResponseBadRequst  (400) - If the request does not have the required GET arguments
                Http404                (404) - If the requested phrase has no available video clips
                HttpResponeServerError (500) - If some problem occurs in communicating with YouGlish

        Remarks:
            The YouGlish REST API for videos can be found at https://youglish.com/api/doc/rest/videos
    """
    ENDPOINT : str = 'https://youglish.com/api/v1/videos/search?{}'

    response : Response

    params : dict[str,str] = {
        'key' : api_keys.YOUGLISH,
        'query' : request.GET.get('phrase', ''),
        'lg' : 'english',
        'accent' : request.GET.get('accent', ''),
        'restricted' : 'yes',
        'page' : request.GET.get('page', '1'),
    }

    if not params['query']:
        return HttpResponseBadRequest()
    
    response = get(ENDPOINT, params=params)
    
    # This try-except is here in order to ensure whatever YouGlish returns is valid json
    # ex: bad api key gives a text response, not json
    try:
        json = response.json()
    except(ValueError):
        return HttpResponseServerError()
    
    if not 'total_results' in json:
        return HttpResponseServerError()
    if json['total_results'] == 0:
        return Http404("No clips available")

    return JsonResponse(json)
