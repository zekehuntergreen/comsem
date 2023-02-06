/**
 * This file is intended to be used when audio must be recorded without user controls
 * No functions are provided to retrieve a transcription of the audio from the server
 */

var audioBlob;
var recorder;

function initializeRecorder() {

    if (!Recorder.isRecordingSupported()) {
        return console.log("Recording features are not supported in your browser.");
    }

    recorder = new Recorder({
        monitorGain: parseInt(monitorGain.value, 10),
        numberOfChannels: parseInt(numberOfChannels.value, 10),
        encoderBitRate: parseInt(bitRate.value, 10),
        encoderSampleRate: parseInt(encoderSampleRate.value, 10),
        encoderPath: encoderPath, // declared in templates
    });

    recorder.addEventListener("start", () => {
        console.log('Recorder is started');
    });

    recorder.addEventListener("stop", () => {
        console.log('Recorder is stopped');
    });

    recorder.addEventListener("pause", () => {
        console.log('Recorder is paused');
    });

    recorder.addEventListener("resume", () => {
        console.log('Recorder is resuming');
    });

    recorder.addEventListener("streamError", (e) => {
        console.error('streamError: ' + e.error.name);
    });

    recorder.addEventListener("streamReady", () => {
        console.log('Audio stream is ready.');
    });

    recorder.addEventListener("dataAvailable", (e) => {
        // audioBlob is the variable name that should be used to reference the audio in other scripts
        audioBlob = new Blob([e.detail], { type: 'audio/ogg' });
        console.log('Audio is ready');
    });

    recorder.initStream();
}
