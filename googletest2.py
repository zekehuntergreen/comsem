import base64
import googleapiclient.discovery

with open("tori_voiceover.mp3", 'rb') as speech:
    # Base64 encode the binary audio file for inclusion in the JSON
    # request.
    speech_content = base64.b64encode(speech.read())

# Construct the request
service = googleapiclient.discovery.build('speech', 'v1')
service_request = service.speech().recognize(
    body={
        "config": {
            "encoding": "LINEAR16",  # raw 16-bit signed LE samples
            "sampleRateHertz": 16000,  # 16 khz
            "languageCode": "en-US",  # a BCP-47 language tag
        },
        "audio": {
            "content": speech_content
            }
        })
