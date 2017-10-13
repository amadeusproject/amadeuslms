$(function () {
	var locale = $("body").data('lang');

	if (!$("#sidebar-menu-div").children().length > 0) {
		//$("#sidebar-menu-div").remove();
		$("#page_content").switchClass('col-md-11', 'col-md-12', 0);
		$("#page_content").switchClass('col-lg-11', 'col-lg-12', 0);
	}
	
	$('.datetime-picker').datetimepicker({
		locale: locale
	});

	$('.date-picker').datetimepicker({
		locale: locale,
		format: 'L'
	});

	$('.text_wysiwyg').summernote({
	    height: 200,
	    lang: new_lang,
	    disableDragAndDrop: true,
	});

	$('[data-toggle="tooltip"]').tooltip({
		trigger: 'hover'
	});

	$('.navbar-header, .search-responsive-collapse .search_mask').click(function (e) {
		if ($(e.target).parent().is($(".mobile_search")) || $(e.target).is($("#mobile_search_btn"))) {
			return;
		}

		if ($('.search-responsive-collapse').hasClass('in')) {
			$("input#mobile_search_btn").click();
			$('.search-responsive-collapse').collapse('hide');
		}
	});

	$('ul.breadcrumb').before('<input id="mobile_breadcrumb_btn" type="checkbox" />');
	$('ul.breadcrumb').after('<div class="bread_mask"></div>');
	$('ul.breadcrumb').wrap('<label for="mobile_breadcrumb_btn" class="bread_label"></label>')

	$('.navbar-header, .bread_mask').click(function (e) {
		if ($('.bread_mask').is(':visible')) {
			$("input#mobile_breadcrumb_btn").click();
		}
	});

	$('ul.breadcrumb li').click(function (e) {
		if ($(this).find('a').length > 0) {
			e.preventDefault();

			window.location = $(this).find('a').attr('href');
		}
		//$(this).find('a').click();
	});

	$('.menu_mask').click(function () {
		$("input#mobile_menu_btn").click();
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
