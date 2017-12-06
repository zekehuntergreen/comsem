
// ARRAY OF EXPRESSIONS

var showNavigationWarning = false;


// because of audio, we must send a formdata object
var worksheetFormData = new FormData();
var expressionsJSON;

var DEBUG = false;


// draw table of current expressions using expressions array AND update the hidden input with jsonified version
function drawExpressionsTable(){
	var tableString = ""
	if (expressions.length > 0) {

		 tableString = "<table class='table table-hover'><thead><tr><th>#</th><th>Student</th><th>Expression</th><th></th></tr></thead><tbody name='expressionTable'>"

		 var expressionCounter = 1;

	 	for (var i = 0; i < expressions.length; i++) {

	 		currentExpression = expressions[i];

			if(!currentExpression['to_delete']){
				tableString += "<tr expressionID='" + currentExpression['id'] + "' index='" + i + "'><td>" + expressionCounter + "</td><td>"

				if (currentExpression['student_name']){
					tableString += currentExpression['student_name'];
				} else {
					tableString +="<b>All-Do</b>";
				}

				tableString += "<td>" + currentExpression['expression'] + "</td>";


				tableString += "<td><button class='btn btn-sm btn-outline-primary editExpression'><i class='fa fa-pencil-square-o'></i></button> <button class='btn btn-sm btn-outline-danger deleteExpression'><i class='fa fa-trash-o'></i></button></td></tr>";

				expressionCounter++;
			}


		}

		tableString += "</tbody></table>";
	} else {

		tableString += "<h4>No Expressions</h4>";

	}

	$('#expressionsTableContainer').html(tableString)

	// bind edit button to it's function - (index doesn't necessarily line up with array because of deleted expressions)
	$('.editExpression').on('click', function(e){
		var index = $(this).parents('tr').attr('index')
		populateEditor(index);
	});

	// bind edit button to it's function
	$('.deleteExpression').on('click', function(e){
		var index = $(this).parents('tr').attr('index')
		expressions[index]['to_delete'] = 1;
		drawExpressionsTable();

		showNavigationWarning = true;

	});

	// UPDATE HIDDEN INPUT WITH JSONIFIED EXPRESSIONS
	expressionsJSON = JSON.stringify(expressions);



}
drawExpressionsTable() // initial call



function populateEditor(index){

	$('#expressionsTableContainer tr').removeClass('cs-active');
	$('#expressionsTableContainer [index=' + index  + ']').addClass('cs-active');

	// prefill the form if we are editing
	if (index != -1) {


		var currentExpression = expressions[index];
		var currentExpressionID = currentExpression['id'];

		// what should the src of the audio element be?
		var audioURL = "";

		if (currentExpression['reformulationAudioBlobSrc']){
			// editing an expression that was saved THIS TIME, not yet in db and file system
			audioURL = currentExpression['reformulationAudioBlobSrc'];

		} else {
			// editing an expression that was saved and in db and file system
			audioURL = calculateAudioURL( {'expressionID': currentExpressionID} )
		}


		$('#expressionIndex').val(index);
		$('#expressionID').val(currentExpressionID);
		if(currentExpression['student_id']){
			$('#studentID').val(currentExpression['student_id']);
		} else {
			$('#studentID').val(0);
		}

		// $('[name=allDo][value=' + currentExpression['allDo'] + ']').prop('checked', true);
		$('#expression').val(currentExpression['expression']);
		$('#reformulation').val(currentExpression['reformulation']);
		$('#contextVocabulary').val(currentExpression['context_vocabulary']);
		$('#pronunciation').val(currentExpression['pronunciation']);

		if( currentExpression['reformulation_audio'] == '0'){

			$('#recordingslist').html("");
			$('#deleteRecordingButton').hide();

		} else {

			// it's important that the audio element has id=audioElement
			$('#recordingslist').html("<audio controls id='audioElement' src='" + audioURL + "' type='audio/mpeg'></audio>");
			$('#deleteRecordingButton').show();

		}

		$('#newExpressionHeader').hide()
		$('#editExpressionHeader').show()

	} else {

		$('#expressionIndex').val(-1);
		$('#expressionID').val(0);
		$('#studentID').val(0);
		// $('[name=allDo][value=0]').prop('checked', true);
		$('#expression').val("");
		$('#reformulation').val("");
		$('#contextVocabulary').val("");
		$('#pronunciation').val("");

		$('#newExpressionHeader').show();
		$('#editExpressionHeader').hide();
		$('#recordingslist').html("");
		$('#deleteRecordingButton').hide();

	}

	// show the form
	$('#ExpressionEditor').slideDown()

}





// add the updated/created expression to the array and draw the table
$("#saveExpression").click(function(e){

	if( $("#expression").val().trim() == "" ){
		// must have a valid expression
		alert("Please enter an expression")
		return;
	}

	var expressionID = $("#expressionID").val();
	var expressionIndex = $("#expressionIndex").val();

	var reformulation_audio = $("#recordingslist #audioElement").length > 0 ? 1 : 0

	student_id = $("#studentID").val() == "0" ? null : $("#studentID").val()

	var expressionObj = {
		expression: $("#expression").val(),
		id: expressionID,
		student_id: student_id,
		student_name: student_id ? $("#studentID option:selected").html() : "", // only for display purposes
		context_vocabulary: $("#contextVocabulary").val(),
		reformulation_text: $("#reformulation").val(),
		pronunciation: $("#pronunciation").val(),
		reformulation_audio: reformulation_audio,
	}

	// always save blob src so that they can edit again
	expressionObj['reformulationAudioBlobSrc'] = $("#recordingslist #audioElement").attr('src');

	if (expressionIndex == -1) {
		// append expression onto array - need to save the index for audio recording below
		expressionIndex = expressions.push(expressionObj) - 1;

	} else {
		// find the expression we are editing, replace it
		expressions[expressionIndex] = expressionObj;
	}

	// handle audio reformulation seperately
	if(reformulation_audio){
		audioReformulationKey = 'audio_ref_' + expressionIndex;
		worksheetFormData.append(audioReformulationKey, audioReformulationBlob); // audioReformulationBlob from ComSemRecording.js

	}

	// update expressions table, put expressions array into hidden input
	drawExpressionsTable();


	// clear editor
	$("#ExpressionEditor").slideUp();

	showNavigationWarning = true; // change to worksheet, show warning if they redirect

});



$(function(){

	// call SaveWorksheet.php then redirect to myCourses page.
	$('#editWorksheetForm').submit(function(e){
		e.preventDefault();

		// populate formdata obj
		worksheetFormData.append( 'course_id', $("#course_id").val() );
		worksheetFormData.append( 'worksheet_id', $("#worksheet_id").val() );
		worksheetFormData.append( 'topic', $("#topic").val() );
		worksheetFormData.append( 'display_original', $("#display_original").prop('checked') );
		worksheetFormData.append( 'display_reformulation_text', $("#display_reformulation_text").prop('checked') );
		worksheetFormData.append( 'display_reformulation_audio', $("#display_reformulation_audio").prop('checked') );
		worksheetFormData.append( 'display_all_expressions', $("[name=display_all_expressions]:checked").val() );
		worksheetFormData.append( 'expressions', expressionsJSON);
		worksheetFormData.append( 'MAX_FILE_SIZE', 10000000); // 10 mb


		// don't show the warning
		showNavigationWarning = false;

		$('#uploadingMessage').slideDown(); // show the message - uploading can take a little while on live site

		$.ajax({
			type: "POST",
			url: save_url,
			data: worksheetFormData,
			processData: false,
			contentType: false,
			success: function(response){
				if(DEBUG){
					console.log(response)
				} else {
					console.log(response)
					location.href=redirect_url
				}
			},
			failure: function(response){
				showErrorMessage(response)
			}
		});
	})

	$('#newExpressionButton').on('click', function(e){
		populateEditor(-1); // -1 means new expression
	});

});

// if they have made changes without saving, warn them
window.addEventListener("beforeunload", function (e) {
	if (showNavigationWarning) {
		var confirmationMessage = 'It looks like you have been editing this worksheet. If you leave before saving, your changes will be lost.';

		(e || window.event).returnValue = confirmationMessage; //Gecko + IE
		return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
	}
});

function inspectFormData(){
    for (var pair of worksheetFormData.entries()) {
        console.log(pair[0]+ ', ' + pair[1]);
    }
}
