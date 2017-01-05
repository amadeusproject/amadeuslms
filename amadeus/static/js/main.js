var locale = navigator.language || navigator.userLanguage;

$('.date-picker').datepicker({ 
	language: locale,
});

$(function () {
	//Dropdown menu collapse
	$('.dropdown-accordion').on('click', 'a[data-toggle="collapse"]', function (event) {
        event.preventDefault();
        event.stopPropagation();
        $($(this).data('parent')).find('.panel-collapse.in').collapse('hide');
        $($(this).attr('href')).collapse('show');
    });
});