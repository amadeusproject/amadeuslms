$(function () {
    getAnswered();
});

function getAnswered() {
	var container = $("#reports"),
		list = container.find('.answered_data'),
		holder = list.parent().find('.holder');

	if (list.children().length == 0) {
		var url = list.parent().data('url');

		$.ajax({
            url: url,
            success: function (data) {
                list.html(data);

                // var form = list.find('.form_search');

                // form.submit(function () {
                // 	searchHistory(panel_id);

                // 	return false;
                // });
                $('#answered_table').DataTable({
                    "dom": "frtip",
                    "language": dataTablei18n
                });
                // var items = $("#answered_table").children(":visible").length;

                // if (items > 10) {
                //     holder.jPages({
                //         containerID : "answered_table",
                //         perPage: 10,
                //         previous: "«",
                //         next: "»",
                //         midRange: 5
                //     });
                // }
            }
        });
	} else {
        $('#answered_table').DataTable();
		// var items = $("#answered_table").children(":visible").length;

  //       if (items > 10) {
  //           holder.jPages({
  //               containerID : "answered_table",
  //               perPage: 10,
  //               previous: "«",
  //               next: "»",
  //               midRange: 5
  //           });
  //       }
	}

    container.find('.answered_link').addClass('active');

  	container.find('.answered').attr('style', 'display: block');
}