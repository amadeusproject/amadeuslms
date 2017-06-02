$(document).ready(function(){
	d = new Date();
	d.setDate(d.getDate() - 30);
	$('#init_date').datetimepicker({
		defaultDate: d,
	});
    $('#end_date').datetimepicker({
        useCurrent: false, //Important! See issue #1075
        defaultDate: new Date()
    });
    $("#init_date").on("dp.change", function (e) {
        $('#end_date').data("DateTimePicker").minDate(e.date);
        end_date = $("#end_date").data("DateTimePicker").date();
        log.refresh_log_data(e.date, end_date);
    });
    $("#end_date").on("dp.change", function (e) {
        $('#init_date').data("DateTimePicker").maxDate(e.date);
        //when the user updates the second one we build the log table
        init_date = $("#init_date").data("DateTimePicker").date();
        log.refresh_log_data(init_date, e.date);
    });
    //initialize the table with log from last 30 days
    init_date = $("#init_date").data("DateTimePicker").date();
   	end_date = $("#end_date").data("DateTimePicker").date();
   	log.refresh_log_data(init_date, end_date);
});




var log = {
	
	refresh_log_data: function(init_date, end_date){
		$.get("/dashboards/get_log_data", {init_date: init_date.format("YYYY-MM-DD HH:mm"), end_date: end_date.format("YYYY-MM-DD HH:mm")}).done(function(data){
			log.render_table("log-body", data);
		})
	},
	render_table: function(target_id, data){
		table_body = $('#' + target_id);

		tables = $('#log-table_wrapper');
		if (tables.length > 0){
			$(tables).remove();
		}


		content = "<table id='log-table' class='table table-striped table-bordered'>";
		//load row names at the top 
		content += "<thead><th> Datetime </th> <th> Usuário </th> <th> Components </th> <th> Recurso </th><th> Ação </th>"
			+ "<th> Categoria </th> <th> Assunto </th> <th> Contexto </th></thead>"
		//build row html data
		data.forEach(function(datum){
			content += "<tr>" + html_helper.row_builder(datum) + "</tr>";
		});

		content += "</table>";

		$(table_body).append(content);

		/*$('#log-table').hpaging({
			"limit": 20, //maximum number of elements per page
		});*/

		$('#log-table').DataTable();

	},
}


var html_helper = {
	row_builder: function(datum){
		//build each table row for each log record
		result = "";
		result = "<td>" + datum.datetime + "</td>" + "<td>" + datum.user + "</td>" + "<td>" + datum.component + "</td>"
		+ "<td>" + datum.resource + "</td>" + "<td>" + datum.action + "</td>" + "<td>" + datum.context.category_name + "</td>"
		+ "<td>" + datum.context.subject_name + "</td>" + "<td>"+ datum.context + "</td>";
		return result;
	}
}