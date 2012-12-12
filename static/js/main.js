(function($){
	$('form').find('input[name="file"]').on('change', function() {
		var filename = $(this).val().split("\\").pop();
		var ext = filename.split(".").pop();
		console.log(ext);
		var text = $(this).siblings('span');
		if(ext != "csv") {
			$(this).val("");
			text.addClass('error').text("CSVs only!");
		} else {
			text.removeClass('error').text(filename);
		}
	});
})($)
