/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

$('.pendencies-content').on('show.bs.collapse', function(e) {
    if($(this).is(e.target)){
        var panel_id = $(this).data('id'),
        	pendencies = $(this).find('.pendencies'),
        	history = $(this).find('.history'),
        	btn = $(this).parent().find('.fa-angle-right');

        btn = btn[0];
        
        $(btn).switchClass("fa-angle-right", "fa-angle-down", 250, "easeInOutQuad");

        getPendencies(panel_id);
    }
});

$('.pendencies-content').on('shown.bs.collapse', function (e) {
    if($(this).is(e.target)){
        var breadcrumb = $(".breadcrumb")[0];
        var li = $(breadcrumb).find('li:last-child');
        var li_text = $(li).html();
        var url = $("#pend_url").val();
        var new_li = $(li).clone();
        
        new_li.html($(this).parent().find('.panel-title').data('title'));

        $(li).html("<a href='" + url + "'>" + li_text + "</a>");
        $(li).append("<span class='divider'>/</span>");

        new_li.appendTo(breadcrumb);
    }
});

$('.pendencies-content').on('hidden.bs.collapse', function(e) {
    if($(this).is(e.target)){
        var btn = $(this).parent().find('.fa-angle-down');
        
        btn = btn[0];
        
        $(btn).switchClass("fa-angle-down", "fa-angle-right", 250, "easeInOutQuad");

        var breadcrumb = $(".breadcrumb")[0];

        $(breadcrumb).find('li:last-child').remove();

        var li = $(breadcrumb).find('li:last-child');
        var text = $(li).find('a').text();

        $(li).html(text);

    	var panel_id = $(this).data('id'),
        	pendencies = $(this).find('.pendencies'),
        	history = $(this).find('.history'),
        	p_holder = pendencies.find('.holder'),
        	h_holder = history.find('.holder');

        
        var p_items = pendencies.find('.pendencies-cards').children(":visible").length;

        if (p_items > 10) {
            p_holder.jPages("destroy");
        }

        var h_items = history.find("#history_table_" + panel_id).children(":visible").length;

        if (h_items > 10) {
        	h_holder.jPages("destroy");
        }

        var url = pendencies.find('.view_log_url').val();
        var log_id = pendencies.find('.view_log_id').val();

        if (typeof(url) != 'undefined') {
            $.ajax({
                url: url,
                data: {'action': 'close', 'log_id': log_id},
                dataType: 'json',
                success: function (data) {
                    console.log(data.message);
                },
                error: function (data) {
                    console.log(data);
                }
            });
        }

        var hist_url = history.find('.hist_log_url').val();
        var hist_log_id = history.find('.hist_log_id').val();

        if (typeof(hist_url) != 'undefined' && hist_log_id != "") {
            $.ajax({
                url: hist_url,
                data: {'action': 'close', 'log_id': hist_log_id},
                dataType: 'json',
                success: function (data) {
                    console.log(data.message);
                },
                error: function (data) {
                    console.log(data);
                }
            });
        }
    }
});

function getPendencies(panel_id) {
	var list = $("#pendencies_list_" + panel_id),
		holder = list.parent().find('.holder');

	if (list.children().length == 0) {
		var url = list.parent().data('url');

		$.ajax({
            url: url,
            success: function (data) {
                list.html(data);

                var items = list.children(":visible").length;

                if (items > 10) {
                    holder.jPages({
                        containerID : "pendencies_list_" + panel_id,
                        perPage: 10,
                        previous: "«",
                        next: "»",
                        midRange: 5
                    });
                }

                metaFunctions();
            }
        });
	} else {
		var items = list.children(":visible").length;

        if (items > 10) {
            holder.jPages({
                containerID : "pendencies_list_" + panel_id,
                perPage: 10,
                previous: "«",
                next: "»",
                midRange: 5
            });
        }

        metaFunctions();
	}

    var url = list.parent().find('.view_log_url').val();
    var log_input = list.parent().find('.view_log_id');

    if (typeof(url) != 'undefined') {
        $.ajax({
            url: url,
            data: {'action': 'open'},
            dataType: 'json',
            success: function (data) {
                log_input.val(data.log_id);
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    var hist_url = list.parent().parent().find('.hist_log_url').val();
    var hist_log_id = list.parent().parent().find('.hist_log_id').val();

    if (typeof(hist_url) != 'undefined' && hist_log_id != "") {
        $.ajax({
            url: hist_url,
            data: {'action': 'close', 'log_id': hist_log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
                list.parent().parent().find('.hist_log_id').val("");
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

	list.parent().parent().find('.history').attr('style', 'display: none');
	list.parent().attr('style', 'display: block');

	list.parent().parent().find('.pendencies_link').addClass('active');
	list.parent().parent().find('.history_link').removeClass('active');
}

function getHistory(panel_id) {
	var container = $("#subject_" + panel_id),
		list = container.find('.history_data'),
		holder = container.find('.holder');

	if (list.children().length == 0) {
		var url = list.parent().data('url');

		$.ajax({
            url: url,
            success: function (data) {
                list.html(data);

                var form = list.find('.form_search');

                form.submit(function () {
                	searchHistory(panel_id);

                	return false;
                });

                var items = $("#history_table_" + panel_id).children(":visible").length;

                if (items > 10) {
                    holder.jPages({
                        containerID : "history_table_" + panel_id,
                        perPage: 10,
                        previous: "«",
                        next: "»",
                        midRange: 5
                    });
                }
            }
        });
	} else {
		var items = $("#history_table_" + panel_id).children(":visible").length;

        if (items > 10) {
            holder.jPages({
                containerID : "history_table_" + panel_id,
                perPage: 10,
                previous: "«",
                next: "»",
                midRange: 5
            });
        }
	}

    var url = container.find('.view_log_url').val();
    var log_id = container.find('.view_log_id').val();

    if (typeof(url) != 'undefined') {
        $.ajax({
            url: url,
            data: {'action': 'close', 'log_id': log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
                container.find('.view_log_id').val("");
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    var hist_url = container.find('.hist_log_url').val();
    var hist_log_input = container.find('.hist_log_id');

    if (typeof(hist_url) != 'undefined') {
        $.ajax({
            url: hist_url,
            data: {'action': 'open'},
            dataType: 'json',
            success: function (data) {
                hist_log_input.val(data.log_id);
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

	container.find('.pendencies_link').removeClass('active');
	container.find('.history_link').addClass('active');

	container.find('.history').attr('style', 'display: block');
	container.find('.pendencies').attr('style', 'display: none');
}

function searchHistory(panel_id) {
	var container = $("#subject_" + panel_id),
		url = container.find('.history').data('url'),
		list = container.find('.history_data'),
		form = container.find('.form_search'),
		holder = container.find('.holder');

	$.ajax({
        url: url,
        data: form.serialize(),
        success: function (data) {
            list.html(data);

            var form = list.find('.form_search');

            form.submit(function () {
            	searchHistory(panel_id);

            	return false;
            });

            var items = $("#history_table_" + panel_id).children(":visible").length;

            holder.jPages("destroy");

            if (items > 10) {
                holder.jPages({
                    containerID : "history_table_" + panel_id,
                    perPage: 10,
                    previous: "«",
                    next: "»",
                    midRange: 5
                });
            }
        }
    });
}

function orderBy(panel_id, order) {
	var container = $("#subject_" + panel_id),
		url = container.find('.history').data('url'),
		list = container.find('.history_data'),
		search = container.find('input[name="search"]').val(),
		holder = container.find('.holder');

	$.ajax({
        url: url,
        data: {'order_by': order, 'search': search},
        success: function (data) {
            list.html(data);

            var form = list.find('.form_search');

            form.submit(function () {
            	searchHistory(panel_id);

            	return false;
            });

            var items = $("#history_table_" + panel_id).children(":visible").length;

            if (items > 10) {
                holder.jPages({
                    containerID : "history_table_" + panel_id,
                    perPage: 10,
                    previous: "«",
                    next: "»",
                    midRange: 5
                });
            }
        }
    });
}

function metaFunctions() {
	var locale = navigator.language || navigator.userLanguage;

    $('[data-toggle="popover"]').popover({
    	html: true,
        content: function () {
            return $(".popover").html();
        }
	}).on('show.bs.popover', function (e) {
		$('[data-toggle="popover"]').not(e.target).popover('hide');
	}).on('shown.bs.popover', function (e) {
		if($(this).is(e.target)){
			var popover = $(this),
				datetime = popover.parent().find('.datetimepicker'),
				form = popover.parent().find('form:visible'),
				cancel = popover.parent().find('.cancel:visible'),
				save = popover.parent().find('.save:visible');

			if (typeof(datetime.data("DateTimePicker")) != "undefined") {
				datetime.data("DateTimePicker").destroy();
			}
		    
		    datetime.datetimepicker({
		    	format: "YYYY-MM-DD HH:mm",
		    	locale: locale,
		        inline: true,
		        sideBySide: false
		    });

		    cancel.on("click", function () {
		    	popover.popover('hide');
		    });	

		    save.on("click", function (e) {
                e.preventDefault();
                e.stopImmediatePropagation();

		    	var meta = datetime.data('date'),
		    		url = form.attr('action'),
		    		method = form.attr('method'),
		    		token = form.find('input[name="csrfmiddlewaretoken"]').val(),
		    		notification = form.find('input[name="id"]').val();
		    					    	
		    	$.ajax({
		    		url: url,
		    		method: method,
		    		data: {'csrfmiddlewaretoken': token, 'meta': meta, 'id': notification},
		    		dataType: 'json',
		    		success: function (response) {
		    			if (response.error) {
		    				alertify.error(response.message);
		    			} else {
		    				alertify.success(response.message);
		    				popover.popover('hide');
		    			}
		    		}
		    	});
		    });
		}
	}).on('hide.bs.popover', function (e) {
		if($(this).is(e.target)){
			var popover = $(this),
				datetime = popover.parent().find('.datetimepicker');

			if (typeof(datetime.data("DateTimePicker")) != "undefined") {
				datetime.data("DateTimePicker").destroy();
			}

			datetime.html('');
		}
	}).on('hidden.bs.popover', function (e) {
	    $(e.target).data("bs.popover").inState.click = false;
	});
}