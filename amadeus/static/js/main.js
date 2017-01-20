var locale = navigator.language || navigator.userLanguage;

$('.datetime-picker').datetimepicker({
	locale: locale
});

$('.date-picker').datetimepicker({
	locale: locale,
	format: 'L'
});

$('.text_wysiwyg').summernote({
    height: 200
});

$(function () {
	$('[data-toggle="tooltip"]').tooltip();

	//Dropdown menu collapse
	$('.dropdown-accordion').on('click', 'a[data-toggle="collapse"]', function (event) {
        event.preventDefault();
        event.stopPropagation();
        $($(this).data('parent')).find('.panel-collapse.in').collapse('hide');
        $($(this).attr('href')).collapse('show');
    });
});