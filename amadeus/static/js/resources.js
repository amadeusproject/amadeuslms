/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

$('#id_groups').multiSelect({
  selectableHeader: "<input type='text' class='search-input category-search-users' autocomplete='off' placeholder=' '>",
  selectionHeader: "<input type='text' class='search-input category-search-users' autocomplete='off' placeholder=''>",
  afterInit: function(ms){
	var that = this,
		$selectableSearch = that.$selectableUl.prev(),
		$selectionSearch = that.$selectionUl.prev(),
		selectableSearchString = '#'+that.$container.attr('id')+' .ms-elem-selectable:not(.ms-selected)',
		selectionSearchString = '#'+that.$container.attr('id')+' .ms-elem-selection.ms-selected';

	that.qs1 = $selectableSearch.quicksearch(selectableSearchString)
	.on('keydown', function(e){
	  if (e.which === 40){
		that.$selectableUl.focus();
		return false;
	  }
	});

	that.qs2 = $selectionSearch.quicksearch(selectionSearchString)
	.on('keydown', function(e){
	  if (e.which == 40){
		that.$selectionUl.focus();
		return false;
	  }
	});
  },
  afterSelect: function(){
	this.qs1.cache();
	this.qs2.cache();
  },
  afterDeselect: function(){
	this.qs1.cache();
	this.qs2.cache();
  }
});// Used to create multi-select css style

$('#id_students').multiSelect({
  selectableHeader: "<input type='text' class='search-input category-search-users' autocomplete='off' placeholder=' '>",
  selectionHeader: "<input type='text' class='search-input category-search-users' autocomplete='off' placeholder=''>",
  afterInit: function(ms){
	var that = this,
		$selectableSearch = that.$selectableUl.prev(),
		$selectionSearch = that.$selectionUl.prev(),
		selectableSearchString = '#'+that.$container.attr('id')+' .ms-elem-selectable:not(.ms-selected)',
		selectionSearchString = '#'+that.$container.attr('id')+' .ms-elem-selection.ms-selected';

	that.qs1 = $selectableSearch.quicksearch(selectableSearchString)
	.on('keydown', function(e){
	  if (e.which === 40){
		that.$selectableUl.focus();
		return false;
	  }
	});

	that.qs2 = $selectionSearch.quicksearch(selectionSearchString)
	.on('keydown', function(e){
	  if (e.which == 40){
		that.$selectionUl.focus();
		return false;
	  }
	});
  },
  afterSelect: function(){
	this.qs1.cache();
	this.qs2.cache();
  },
  afterDeselect: function(){
	this.qs1.cache();
	this.qs2.cache();
  }
});// Used to create multi-select css style

$('.collapse').on('show.bs.collapse', function (e) {
	if($(this).is(e.target)){
		var btn = $(this).parent().find('.fa-angle-right');

		btn.switchClass("fa-angle-right", "fa-angle-down", 250, "easeInOutQuad");
	}
});

$('.collapse').on('hide.bs.collapse', function (e) {
	if($(this).is(e.target)){
		var btn = $(this).parent().find('.fa-angle-down');

		btn.switchClass("fa-angle-down", "fa-angle-right", 250, "easeInOutQuad");
	}
});

$('.begin_date_input').on('click', function () {
	var checkbox = $(this).parent().parent().find('.begin_date');

	$(checkbox).prop('checked', true);
});

$('.end_date_input').on('click', function () {
	var checkbox = $(this).parent().parent().find('.end_date');

	$(checkbox).prop('checked', true);
});

$('.limit_date_input').on('click', function () {
	var checkbox = $(this).parent().parent().find('.limit_date');

	$(checkbox).prop('checked', true);
});

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