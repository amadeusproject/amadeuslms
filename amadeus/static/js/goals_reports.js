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

    setBreadcrumb(unansweredBread);
}

function setBreadcrumb(text) {
    var breadcrumb = $(".breadcrumb")[0],
        li = $(breadcrumb).find('li:last-child');
        
    $(li).html(text);
}