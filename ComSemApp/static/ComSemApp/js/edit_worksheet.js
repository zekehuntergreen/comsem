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
		$('#ExpressionEditor').show()

		scrollToDiv('#ExpressionEditorCardBox')

		// focus on first element of the form
		$('#studentID').focus()
	})

}

$(function(){

	$('#newExpressionButton').on('click', function(e){
		$('#expressionsTableContainer tr').removeClass('cs-active');
		populateEditor(expression_create_url);
	});

});


function inspectFormData(worksheetFormData){
	for (var pair of worksheetFormData.entries()) {
		console.log(pair[0]+ ', ' + pair[1]);
	}
}
