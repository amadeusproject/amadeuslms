$(function () {
	var locale = $("body").data('lang');
	
	$('.datetime-picker').datetimepicker({
		locale: locale
	});

	$('.date-picker').datetimepicker({
		locale: locale,
		format: 'L'
	});

	$('.text_wysiwyg').summernote({
	    height: 200,
	    disableDragAndDrop: true,
	});

	$('[data-toggle="tooltip"]').tooltip({
		trigger: 'hover'
	});

	//Dropdown menu collapse
	$('.dropdown-accordion').on('click', 'a[data-toggle="collapse"]', function (event) {
        event.preventDefault();
        event.stopPropagation();
        $($(this).data('parent')).find('.panel-collapse.in').collapse('hide');
        $($(this).attr('href')).collapse('show');
    });
});

var change_language = {
	post: function(url, language){
		$.post(url, language ,function(data){
				window.location.href= window.location.href;
		});
	}
}
