// include in pages that need to record / save / access audio files

var recorder;

start.addEventListener( "click", function(){ recorder.start(); });
pause.addEventListener( "click", function(){ recorder.pause(); });
resume.addEventListener( "click", function(){ recorder.resume(); });
stopButton.addEventListener( "click", function(){ recorder.stop(); });

function initializeRecorder(){

	if (!Recorder.isRecordingSupported()) {
		return screenLogger("Recording features are not supported in your browser.");
	}

	recorder = new Recorder({
		monitorGain: parseInt(monitorGain.value, 10),
		numberOfChannels: parseInt(numberOfChannels.value, 10),
		encoderBitRate: parseInt(bitRate.value,10),
		encoderSampleRate: parseInt(encoderSampleRate.value,10),
		encoderPath: encoderPath, // declared in templates
	});

	recorder.addEventListener( "start", function(e){
		screenLogger('Recorder is started');
		start.disabled = resume.disabled = true;
		pause.disabled = stopButton.disabled = false;
	});

	recorder.addEventListener( "stop", function(e){
		screenLogger('Recorder is stopped');
		false;
		pause.disabled = resume.disabled = stopButton.disabled = start.disabled = true;
	});

	recorder.addEventListener( "pause", function(e){
		screenLogger('Recorder is paused');
		pause.disabled = start.disabled = true;
		resume.disabled = stopButton.disabled = false;
	});

	recorder.addEventListener( "resume", function(e){
		screenLogger('Recorder is resuming');
		start.disabled = resume.disabled = true;
		pause.disabled = stopButton.disabled = false;
	});

	recorder.addEventListener( "streamError", function(e){
		screenLogger('Error encountered: ' + e.error.name );
	});

	recorder.addEventListener( "streamReady", function(e){
		pause.disabled = resume.disabled = stopButton.disabled = true;
		start.disabled = false;
		screenLogger('Audio stream is ready.');
	});

	recorder.addEventListener( "dataAvailable", function(e){
		var dataBlob = new Blob( [e.detail], { type: 'audio/ogg' } );
		audioReformulationBlob = dataBlob; // save the current blob
		var fileName = new Date().toISOString() + ".opus";
		var url = URL.createObjectURL( dataBlob );

		var audio = document.createElement('audio');
		audio.controls = true;
		audio.src = url;
		audio.id = 'audioElement' // important to identify later

		var link = document.createElement('a');
		link.href = url;
		link.download = fileName;
		link.innerHTML = link.download;

		var li = document.createElement('li');
		li.appendChild(link);
		li.appendChild(audio);

		// recordingslist.appendChild(li);

		// changed in order to allow only one recording at a time:
		$('#recordingslist').html(audio);
		$('#deleteRecordingButton').attr('disabled', false);

		initializeRecorder() // need to call function again to re-initialize
	});

	recorder.initStream();
}

function screenLogger(text, data) {
	// log.innerHTML += "\n" + text + " " + (data || '');
	// use console log instead
	console.log( text + " " + (data || '') )
}




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
		audioURL = "/efs/ExpressionReformulations/" + audioReformulationDirName + "/" + audioReformulationFileName + ".ogg";
	} else if(attemptID){
		audioURL = "/efs/AttemptReformulations/" + audioReformulationDirName + "/" + audioReformulationFileName + ".ogg";
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
		$(this).attr('disabled', true)
	});
})
