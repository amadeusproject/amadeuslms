// check if browser supports drag n drop
// call initialization file
if (window.File && window.FileList && window.FileReader) {
	Init();
}

// initialize
function Init() {
	var small = $("#id_small_logo"),
		large = $("#id_large_logo"),
		fav = $("#id_favicon"),
		contrast = $("#id_high_contrast_logo"),
		filedrag = $(".filedrag"),
		common = $(".common-file-input");
		
	// file select
	fav.on("change", FileSelectHandler);
	small.on("change", FileSelectHandler);
	large.on("change", FileSelectHandler);
	contrast.on("change", FileSelectHandler);

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
		file_id = parent.data('file_id'),
		submit_btn = $("#theme-form").find("input[type='submit']"),
		max_size = 2*1024*1024;

	parent.removeClass('alert-file');

	var alerts_open = $("#theme-form").find(".alert-file").length;

	if (alerts_open == 0) {
		$(submit_btn).prop('disable', false);
		$(submit_btn).prop('disabled', false);
	}

	$("." + file_id + "-file-errors").hide();
	$("." + file_id + "-file-errors .size").hide();
	$("." + file_id + "-file-errors .format").hide();
	// process all File objects
	for (var i = 0, f; f = files[i]; i++) {
		if (f.size > max_size) {
			$(submit_btn).prop('disable', true);
			$(submit_btn).prop('disabled', true);

			$("." + file_id + "-file-errors").show();
			$("." + file_id + "-file-errors .size").show();

			parent.addClass('alert-file');
		} 

		if (!f.type.match(/^image\//)) {
			$(submit_btn).prop('disable', true);
			$(submit_btn).prop('disabled', true);

			$("." + file_id + "-file-errors").show();
			$("." + file_id + "-file-errors .format").show();

			parent.addClass('alert-file');
		}

		parent.find('.filedrag').html(f.name);
	}
}