$(document).ready(function(){
	$('#init_date').datetimepicker();
    $('#end_date').datetimepicker({
        useCurrent: false //Important! See issue #1075
    });
    $("#init_date").on("dp.change", function (e) {
        $('#end_date').data("DateTimePicker").minDate(e.date);
    });
    $("#end_date").on("dp.change", function (e) {
        $('#init_date').data("DateTimePicker").maxDate(e.date);
        init_date = $("#init_date").data("DateTimePicker").date();
        log.refresh_log_data(init_date, e.date);
    });

   
});




var log = {
	
	refresh_log_data: function(init_date, end_date){
		$.get("/dashboards/get_log_data", {init_date: init_date.format("YYYY-MM-DD HH:mm"), end_date: end_date.format("YYYY-MM-DD HH:mm")}).done(function(data){
			log.render_table("log-body", data);
		})
	},
	render_table: function(target_id, data){
		table_body = $('#' + target_id);

		content = "<table id='log-table'>";

		//load row names at the top 
		
		//build row html data
		data.forEach(function(datum){
			content += "<tr>" + html_helper.row_builder(datum) + "</tr>";
		});

		content += "</table>";

		$(table_body).append(content);
	},
}


var html_helper = {
	row_builder: function(datum){
		result = "";
		result = "<td>" + datum.datetime + "</td>" + "<td>" + datum.user + "</td>" + "<td>" + datum.component + "</td>"
		+ "<td>" + datum.resource + "</td>" + "<td>" + datum.action + "</td>" + "<td>" + datum.context.category_name + "</td>"
		+ "<td>" + datum.context.subject_name + "</td>" + "<td>"+ datum.context + "</td>";
		return result;
	}
}