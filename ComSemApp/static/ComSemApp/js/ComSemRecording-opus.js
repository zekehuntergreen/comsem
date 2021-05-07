/**
 * ComSemRecording-opus
 * This file is included in pages that need to access, save, or record
 * any audio files in ComSem
 *  
 * Changes:
 *		Nate Kirsch (02/09):	Implemented the ajax call within "dataavailable" listener, as 
 *								well as the resultText function
 *		Jalen Tacsiat (02/11):	Changed the resultText function to work on the associated 
 *								Student and teacher pages
 *		Nate Kirsch (02/20):	Cleaned up useless code and added relevent comments
 * 		Joseph Torii (05/02):   Adding more documentation 
 */


// include in pages that need to record / save / access audio files!

var audioReformulationBlob;

var recorder;

start.addEventListener("click", function () { recorder.start(); });
pause.addEventListener("click", function () { recorder.pause(); });
resume.addEventListener("click", function () { recorder.resume(); });
stopButton.addEventListener("click", function () { recorder.stop(); });

function initializeRecorder() {

	if (!Recorder.isRecordingSupported()) {
		return screenLogger("Recording features are not supported in your browser.");
	}

	recorder = new Recorder({
		monitorGain: parseInt(monitorGain.value, 10),
		numberOfChannels: parseInt(numberOfChannels.value, 10),
		encoderBitRate: parseInt(bitRate.value, 10),
		encoderSampleRate: parseInt(encoderSampleRate.value, 10),
		encoderPath: encoderPath, // declared in templates
	});

	recorder.addEventListener("start", function (e) {
		screenLogger('Recorder is started');
		start.disabled = resume.disabled = true;
		pause.disabled = stopButton.disabled = false;
	});

	recorder.addEventListener("stop", function (e) {
		screenLogger('Recorder is stopped');
		false;
		pause.disabled = resume.disabled = stopButton.disabled = start.disabled = true;
	});

	recorder.addEventListener("pause", function (e) {
		screenLogger('Recorder is paused');
		pause.disabled = start.disabled = true;
		resume.disabled = stopButton.disabled = false;
	});

	recorder.addEventListener("resume", function (e) {
		screenLogger('Recorder is resuming');
		start.disabled = resume.disabled = true;
		pause.disabled = stopButton.disabled = false;
	});

	recorder.addEventListener("streamError", function (e) {
		screenLogger('Error encountered: ' + e.error.name);
	});

	recorder.addEventListener("streamReady", function (e) {
		pause.disabled = resume.disabled = stopButton.disabled = true;
		start.disabled = false;
		screenLogger('Audio stream is ready.');
	});

	recorder.addEventListener("dataAvailable", function (e) {
		// dataBlob is stored within the ComSem database
		var dataBlob = new Blob([e.detail], { type: 'audio/ogg' });
		audioReformulationBlob = dataBlob; // save the current blob
		var fileName = new Date().toISOString() + ".opus";
		var url = URL.createObjectURL(dataBlob);

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

		screenLogger('Audio is ready');

		// copyBlob is made specifically to transcribe the user's audio recording
		var copyBlob = new Blob([e.detail], { type: 'audio/wav' });

		// The audioBlob is placed into a FormData to be passed through ajax
		var data = new FormData();
		data.append('audioBlob', copyBlob);

		// The ajax call to transcribe the recorded audio is made
		$.ajax({
			url: '{% url "transcribe_call/" %}',
			type: "POST",
			data: data,
			processData: false,
			contentType: false,
			success: function callback(response) {
				// With the response we paste the text to screen
				resultText(response);
			}
		});

		x = document.getElementById("reformulation");

		// changed in order to allow only one recording at a time:
		$('#recordingslist').html(audio);
		$('#deleteRecordingButton').attr('disabled', false);

		initializeRecorder() // need to call function again to re-initialize
	});

	recorder.initStream();
}

function screenLogger(text, data) {
	console.log(text + " " + (data || ''))
}


/**
 * resultText is called from within the ajax call in the "dataAvailable" listener when there is
 * a response from the python transcribe function
 * @param {*} response is the sentence that the user has just recorded
 */
function resultText(response) {
	// Checking which page the user is accessing
	x = document.getElementById("reformulation");
	y = document.getElementById("CorrectedExpr");

	// "reformulation" will be not be null if the teacher is recording their expression
	if (x != null) {
		x.value = response;
		screenLogger(x.value);
	}
	// "CorrectedExpr" will not be null if the student is attempting to reformulate a sentence
	else if (y != null) {
		y.value = response;
		screenLogger(y.value);
	}
	// The user has accessed this function on a page in which it wasn't intended to be used.
	else {
		screenLogger("document element does not exist")
	}
}




// return the url of the audio based on recording type, expression/attempt ID, and file system in use (live/dev)
function calculateAudioURL(typeObj) {

	var audioURL = null;
	var expressionID = typeObj['expressionID'];
	var attemptID = typeObj['attemptID'];

	var expressionOrAttemptID = expressionID ? expressionID : attemptID;

	var audioReformulationDirName = Math.floor((expressionOrAttemptID / 1000));

	var audioReformulationFileName;

	if (audioReformulationDirName == 0) {
		audioReformulationFileName = expressionOrAttemptID;
	} else {
		audioReformulationFileName = (expressionOrAttemptID % (audioReformulationDirName * 1000));
	}


	if (expressionID) {
		audioURL = "/efs/ExpressionReformulations/" + audioReformulationDirName + "/" + audioReformulationFileName + ".ogg";
	} else if (attemptID) {
		audioURL = "/efs/AttemptReformulations/" + audioReformulationDirName + "/" + audioReformulationFileName + ".ogg";
	}

	return audioURL;
}

function showErrorMessage(text) {
	$('#errorMessage').slideDown();
	$('#errorMsgText').html("<b>Error!</b> " + text);

	$('#uploadingMessage').slideUp();

}

// bind delete recording button
$(function () {
	$('#deleteRecordingButton').click(function () {
		$('#recordingslist').html('');
		$(this).attr('disabled', true)
	});
})
