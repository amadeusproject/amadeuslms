/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

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
