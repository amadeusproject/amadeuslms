/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

$(function () {
    getAnswered();
});

function getAnswered() {
	var container = $("#reports"),
		list = container.find('.answered_data');

	if (list.children().length == 0) {
		var url = list.parent().data('url');

		$.ajax({
            url: url,
            success: function (data) {
                list.html(data);

                $('#answered_table').DataTable({
                    "dom": "Bfrtip",
                    "language": dataTablei18n,
                    buttons: {
                        dom: {
                            container: {
                                className: 'col-md-3'
                            },
                            buttonContainer: {
                                tag: 'h4',
                                className: 'history-header'
                            },
                        },
                        buttons: [
                            {
                                extend: 'csv',
                                text: csvBtnLabeli18n,
                                filename: 'report-answered'
                            }
                        ]
                    }
                });
            }
        });
	}


    var url = container.find('.answ_log_url').val();
    var log_input = container.find('.answ_log_id');

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

    var unan_url = container.find('.unan_log_url').val();
    var unan_log_id = container.find('.unan_log_id').val();

    if (typeof(unan_url) != 'undefined' && unan_log_id != "") {
        $.ajax({
            url: unan_url,
            data: {'action': 'close', 'log_id': unan_log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
                container.find('.unan_log_id').val("");
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    var hist_url = container.find('.hist_log_url').val();
    var hist_log_id = container.find('.hist_log_id').val();

    if (typeof(hist_url) != 'undefined' && hist_log_id != "") {
        $.ajax({
            url: hist_url,
            data: {'action': 'close', 'log_id': hist_log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
                container.find('.hist_log_id').val("");
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    container.find('.answered_link').addClass('active');
  	container.find('.answered').show();

    container.find('.unanswered_link').removeClass('active');
    container.find('.unanswered').hide();

    container.find('.history_link').removeClass('active');
    container.find('.history').hide();

    setBreadcrumb(answeredBread);
}

function getUnanswered() {
    var container = $("#reports"),
        list = container.find('.unanswered_data');

    if (list.children().length == 0) {
        var url = list.parent().data('url');

        $.ajax({
            url: url,
            success: function (data) {
                list.html(data);
                
                $('#unanswered_table').DataTable({
                    "dom": "Bfrtip",
                    "language": dataTablei18n,
                    buttons: {
                        dom: {
                            container: {
                                className: 'col-md-3'
                            },
                            buttonContainer: {
                                tag: 'h4',
                                className: 'history-header'
                            },
                        },
                        buttons: [
                            {
                                extend: 'csv',
                                text: csvBtnLabeli18n,
                                filename: 'report-unanswered'
                            }
                        ],
                    },
                    "columns": [
                        null,
                        null,
                        { "orderable": false },
                    ]
                });

                $("#check_all_rows").click(function () {
                    var checked = this.checked;
                        
                    $('#unanswered_table').find('input[type="checkbox"]').each(function() {
                        this.checked = checked;
                    });
                });
            }
        });
    }

    var url = container.find('.answ_log_url').val();
    var log_id = container.find('.answ_log_id').val();

    if (typeof(url) != 'undefined' && log_id != "") {
        $.ajax({
            url: url,
            data: {'action': 'close', 'log_id': log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
                container.find('.answ_log_id').val("");
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    var unan_url = container.find('.unan_log_url').val();
    var unan_log_input = container.find('.unan_log_id');

    if (typeof(unan_url) != 'undefined') {
        $.ajax({
            url: unan_url,
            data: {'action': 'open'},
            dataType: 'json',
            success: function (data) {
                unan_log_input.val(data.log_id);
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    var hist_url = container.find('.hist_log_url').val();
    var hist_log_id = container.find('.hist_log_id').val();

    if (typeof(hist_url) != 'undefined' && hist_log_id != "") {
        $.ajax({
            url: hist_url,
            data: {'action': 'close', 'log_id': hist_log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
                container.find('.hist_log_id').val("");
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    container.find('.answered_link').removeClass('active');
    container.find('.answered').hide();

    container.find('.unanswered_link').addClass('active');
    container.find('.unanswered').show();

    container.find('.history_link').removeClass('active');
    container.find('.history').hide();

    setBreadcrumb(unansweredBread);
}

function getHistory() {
    var container = $("#reports"),
        list = container.find('.history_data');

    if (list.children().length == 0) {
        var url = list.parent().data('url');

        $.ajax({
            url: url,
            success: function (data) {
                list.html(data);
                
                $('#history_table').DataTable({
                    "dom": "Bfrtip",
                    "language": dataTablei18n,
                    buttons: {
                        dom: {
                            container: {
                                className: 'col-md-3'
                            },
                            buttonContainer: {
                                tag: 'h4',
                                className: 'history-header'
                            },
                        },
                        buttons: [
                            {
                                extend: 'csv',
                                text: csvBtnLabeli18n,
                                filename: 'report-history'
                            }
                        ],
                    },
                });
            }
        });
    }

    var url = container.find('.answ_log_url').val();
    var log_id = container.find('.answ_log_id').val();

    if (typeof(url) != 'undefined' && log_id != "") {
        $.ajax({
            url: url,
            data: {'action': 'close', 'log_id': log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
                container.find('.answ_log_id').val("");
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    var unan_url = container.find('.unan_log_url').val();
    var unan_log_id = container.find('.unan_log_id').val();

    if (typeof(unan_url) != 'undefined' && unan_log_id != "") {
        $.ajax({
            url: unan_url,
            data: {'action': 'close', 'log_id': unan_log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
                container.find('.unan_log_id').val("");
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

    container.find('.answered_link').removeClass('active');
    container.find('.answered').hide();

    container.find('.unanswered_link').removeClass('active');
    container.find('.unanswered').hide();

    container.find('.history_link').addClass('active');
    container.find('.history').show();

    setBreadcrumb(historyBread);
}

function setBreadcrumb(text) {
    var breadcrumb = $(".breadcrumb")[0],
        li = $(breadcrumb).find('li:last-child');
        
    $(li).html(text);
}