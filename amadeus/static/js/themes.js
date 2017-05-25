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
		filedrag = $(".filedrag"),
		common = $(".common-file-input");
		
	// file select
	fav.on("change", FileSelectHandler);
	small.on("change", FileSelectHandler);
	large.on("change", FileSelectHandler);

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
		parent = $(e.target.offsetParent);

	// process all File objects
	for (var i = 0, f; f = files[i]; i++) {
		parent.find('.filedrag').html(f.name);
	}
}