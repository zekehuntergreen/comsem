/**
 * This file is intended to be used when audio must be recorded without user controls
 * No functions are provided to retrieve a transcription of the audio from the server
 */

var audioBlob;
var recorder;

function initializeRecorder() {
    return new Promise((resolve, reject) => {
        if (!Recorder.isRecordingSupported()) {
            reject("Recording features are not supported in your browser.");
        }

        recorder = new Recorder({
            monitorGain: parseInt(monitorGain.value, 10),
            numberOfChannels: parseInt(numberOfChannels.value, 10),
            encoderBitRate: parseInt(bitRate.value, 10),
            encoderSampleRate: parseInt(encoderSampleRate.value, 10),
            encoderPath: encoderPath, // declared in templates
        });

        recorder.addEventListener("streamError", (e) => {
            console.error('streamError: ' + e.error.name);
            if (e.error.name == 'NotAllowedError') {
                reject("Cannot record. Please allow microphone permissions.")
            }
            else {
                reject(e.error.name);
            }
        });

        recorder.addEventListener("streamReady", () => {
            console.log('Audio stream is ready.');
            resolve();
        });

        recorder.addEventListener("dataAvailable", (e) => {
            // audioBlob is the variable name that should be used to reference the audio in other scripts
            audioBlob = new Blob([e.detail], { type: 'audio/ogg' });
            console.log('Audio is ready');
        });

        recorder.initStream();
    });
}
