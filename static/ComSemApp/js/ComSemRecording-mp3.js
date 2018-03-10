// no longer in use after switch to opus format

var audioReformulationBlob;

function __log(e, data) {
	console.log("\n" + e + " " + (data || ''));
}

var audio_context;
var recorder;

function startUserMedia(stream) {
	var input = audio_context.createMediaStreamSource(stream);
	__log('Media stream created.');

	// Uncomment if you want the audio to feedback directly
	// input.connect(audio_context.destination);
	__log('Input connected to audio context destination.');

	config = {
		'bufferLen': 256,
		'numChannels': 1,
	}
	recorder = new Recorder(input, config);

	__log('Recorder initialised.');
}

function startRecording(button) {
	recorder && recorder.record();
	button.disabled = true;
	button.nextElementSibling.disabled = false;
	__log('Recording...');
}

function stopRecording(button) {
	recorder && recorder.stop();
	button.disabled = true;
	button.previousElementSibling.disabled = false;
	__log('Stopped recording.');

	// create an mp3 download link using audio data blob
	createDownloadLink();

	recorder.clear();
}

function createDownloadLink() {
	recorder && recorder.exportWAV(function(blob) {
		audioReformulationBlob = blob; // save the current blob
		var url = URL.createObjectURL(blob);
		var au = document.createElement('audio');
		au.id = "audioElement";

		au.controls = true;
		au.src = url;
		$('#recordingslist').html(au);
		$('#deleteRecordingButton').show();
	});
}

window.onload = function init() {
	try {
		// webkit shim
		window.AudioContext = window.AudioContext || window.webkitAudioContext;
		navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
		window.URL = window.URL || window.webkitURL;

		audio_context = new AudioContext;
		__log('Audio context set up.');
		__log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
	} catch (e) {
		alert('No web audio support in this browser!');
	}

	navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
		__log('No live audio input: ' + e);
	});
};

// return the url of the audio based on recording type, expression/attempt ID, and file system in use (live/dev)
function calculateAudioURL(typeObj){

	var audioURL = null;
	var expressionID = typeObj['expressionID'];
	var attemptID = typeObj['attemptID'];

	var expressionOrAttemptID = expressionID ? expressionID : attemptID;

	var audioReformulationDirName = Math.floor((expressionOrAttemptID / 1000));

	var audioReformulationFileName;

	if(audioReformulationDirName == 0){
		audioReformulationFileName = expressionOrAttemptID;
	} else {
		audioReformulationFileName = (expressionOrAttemptID % (audioReformulationDirName * 1000) );
	}


	if(expressionID){
		audioURL = "/efs/ExpressionReformulations/" + audioReformulationDirName + "/" + audioReformulationFileName + ".mp3";
	} else if(attemptID){
		audioURL = "/efs/AttemptReformulations/" + audioReformulationDirName + "/" + audioReformulationFileName + ".mp3";
	}

	return audioURL;
}

function showErrorMessage(text){
	$('#errorMessage').slideDown();
	$('#errorMsgText').html("<b>Error!</b> " + text);

	$('#uploadingMessage').slideUp();

}

// bind delete recording button
$(function(){
	$('#deleteRecordingButton').click(function(){
		$('#recordingslist').html('');
		$(this).hide()
	});
})
