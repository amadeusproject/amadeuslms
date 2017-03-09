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