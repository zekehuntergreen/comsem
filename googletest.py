import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Instantiates a client
client = speech.SpeechClient()

# The name of the audio file to transcribe
file_name = "efs/reformulations/41c87965-0174-4231-8253-db494f9a8a61.ogg"

# Loads the audio into memory
with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()

audio = types.RecognitionAudio(content=content)

# for i in range(8000, 48001, 2000):
for i in [8000, 12000, 16000, 24000, 48000]:
    print(i)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=i,
        language_code='en-US')

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    print("Recognizing")
    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))
