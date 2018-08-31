// check if browser supports drag n drop
// call initialization file
if (window.File && window.FileList && window.FileReader) {
	Init();
}

// initialize
function Init() {
	var small = $(".file-selector"),
		filedrag = $(".filedrag"),
		common = $(".common-file-input");
		
	// file select
	small.on("change", FileSelectHandler);

	// is XHR2 available?
	var xhr = new XMLHttpRequest();
	if (xhr.upload) {
		// file drop
		filedrag.on("drop", FileSelectHandler);
		filedrag.attr('style', 'display:block');
		common.attr('style', 'display:none');
	}
}

// file selection
function FileSelectHandler(e) {
	var files = e.target.files || e.dataTransfer.files,
		parent = $(e.target.offsetParent),
		max_size = parseInt($(e.target).data("max_size")) * 1024 * 1024,
		submit_btn = $(e.target).closest("form").find("input[type='submit']"),
		mimeTypes = $(e.target).data('mimetypes'),
		file_id = parent.data('file_id');

	if ($(e.target).closest("form").prop('id') == "bulletin") {
		parent.removeClass('alert-file');

		var alerts_open = $(e.target).closest("form").find(".alert-file").length;
		
		if (alerts_open == 0) {
			$(submit_btn).prop('disable', false);
			$(submit_btn).prop('disabled', false);
		}

		$("." + file_id + "-file-errors").hide();
		$("." + file_id + "-file-errors .size").hide();
		$("." + file_id + "-file-errors .format").hide();
	} else {
		$(".client-file-errors").hide();
		$(".size").hide();
		$(".format").hide();
		$(submit_btn).prop('disable', false);
		$(submit_btn).prop('disabled', false);
	}


	// process all File objects
	for (var i = 0, f; f = files[i]; i++) {

		if (f.size > max_size) {
			$(submit_btn).prop('disable', true);
			$(submit_btn).prop('disabled', true);

			if ($(e.target).closest("form").prop('id') == "bulletin") {
				$("." + file_id + "-file-errors").show();
				$("." + file_id + "-file-errors .size").show();

				parent.addClass('alert-file');
			} else {
				$(".client-file-errors").show();
				$(".size").show();
			}
		} 

		if (!mimeTypes.includes(f.type)) {
			$(submit_btn).prop('disable', true);
			$(submit_btn).prop('disabled', true);

			if ($(e.target).closest("form").prop('id') == "bulletin") {
				$("." + file_id + "-file-errors").show();
				$("." + file_id + "-file-errors .format").show();

				parent.addClass('alert-file');
			} else {
				$(".client-file-errors").show();
				$(".format").show();
			}
		}

		parent.find('.filedrag').html(f.name);
	}
}