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
			log.render_table("log_body", data);
		})
	},
	render_table: function(target_id, data){
		table_body = $('#' + target_id);

		data.forEach(function(datum){
			console.log(datum);
		});
	},
}
