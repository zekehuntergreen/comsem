// load the list of expressions for the worksheet
function drawExpressionsTable(){
	console.log("drawing expressions table")
	$('#expressionsTableContainer').load(expression_list_url)
}
drawExpressionsTable() // initial call



function populateEditor(url){
	// url is either expression create or update url

	$("#expression_form").load(url, function(){
		$("#create_or_update_url").val(url)

		initializeRecorder(); // initialize the recorder. function found in ComSemRecording-opus.js

		// show the form
		$('#ExpressionEditor').slideDown()
	})




	// prefill the form if we are editing
	// if (index != -1) {


	// 	var currentExpression = expressions[index];
	// 	var currentExpressionID = currentExpression['id'];

	// 	// what should the src of the audio element be?
	// 	var audioURL = "";

	// 	if (currentExpression['reformulationAudioBlobSrc']){
	// 		// editing an expression that was saved THIS TIME, not yet in db and file system
	// 		audioURL = currentExpression['reformulationAudioBlobSrc'];

	// 	} else {
	// 		// editing an expression that was saved and in db and file system
	// 		audioURL = calculateAudioURL( {'expressionID': currentExpressionID} )
	// 	}


	// 	$('#expressionIndex').val(index);
	// 	$('#expressionID').val(currentExpressionID);
	// 	if(currentExpression['student_id']){
	// 		$('#studentID').val(currentExpression['student_id']);
	// 	} else {
	// 		$('#studentID').val(0);
	// 	}

	// 	$('#all_do').prop('checked', currentExpression['all_do']);
	// 	$('#expression').val(currentExpression['expression']);
	// 	$('#reformulation').val(currentExpression['reformulation']);
	// 	$('#contextVocabulary').val(currentExpression['context_vocabulary']);
	// 	$('#pronunciation').val(currentExpression['pronunciation']);

	// 	if( currentExpression['reformulation_audio'] == '0'){

	// 		$('#recordingslist').html("");
	// 		$('#deleteRecordingButton').hide();

	// 	} else {

	// 		// it's important that the audio element has id=audioElement
	// 		$('#recordingslist').html("<audio controls id='audioElement' src='" + audioURL + "' type='audio/mpeg'></audio>");
	// 		$('#deleteRecordingButton').show();

	// 	}

	// 	$('#newExpressionHeader').hide()
	// 	$('#editExpressionHeader').show()

	// } else {

	// 	$('#expressionIndex').val(-1);
	// 	$('#expressionID').val(0);
	// 	$('#studentID').val(0);
	// 	$('#all_do').prop('checked', false);
	// 	$('#expression').val("");
	// 	$('#reformulation').val("");
	// 	$('#contextVocabulary').val("");
	// 	$('#pronunciation').val("");

	// 	$('#newExpressionHeader').show();
	// 	$('#editExpressionHeader').hide();
	// 	$('#recordingslist').html("");
	// 	$('#deleteRecordingButton').hide();

	// }



}

$(function(){

	$('#newExpressionButton').on('click', function(e){
		$('#expressionsTableContainer tr').removeClass('cs-active');
		populateEditor(expression_create_url);
	});

});

// // if they have made changes without saving, warn them
// window.addEventListener("beforeunload", function (e) {
// 	if (showNavigationWarning) {
// 		var confirmationMessage = 'It looks like you have been editing this worksheet. If you leave before saving, your changes will be lost.';

// 		(e || window.event).returnValue = confirmationMessage; //Gecko + IE
// 		return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
// 	}
// });

function inspectFormData(worksheetFormData){
    for (var pair of worksheetFormData.entries()) {
        console.log(pair[0]+ ', ' + pair[1]);
    }
}
