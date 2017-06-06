$(document).ready(function(){
	charts.most_used_tags('/analytics/get_category_tags/?category_id='+$("#category-selector").val());
	
	$("#category-selector").on("change", function(e){
		//when it changes, the tag chart is replaced and all others are.
		var category_id = $(e.target).val();
		charts.most_used_tags('/analytics/get_category_tags/?category_id='+category_id);


		//first call to month selector
		var month = new Array();
		month[0] = "January";
		month[1] = "February";
		month[2] = "March";
		month[3] = "April";
		month[4] = "May";
		month[5] = "June";
		month[6] = "July";
		month[7] = "August";
		month[8] = "September";
		month[9] = "October";
		month[10] = "November";
		month[11] = "December";
 

		$.get('/analytics/amount_active_users_per_day', { month: month[(new Date()).getMonth()], category_id: category_id  }).done(function(data){
			charts.month_heatmap(data, '#right-side-heatmaps', 'month-chart');
		});

	});





	$('#month_selector').change(function(){

			var date = $(this).val().split("/");
			$.get('/analytics/amount_active_users_per_day', {month: date[0], year: date[1], category_id: $("#category-selector").val() }).done(function(data){
				charts.month_heatmap(data, '#right-side-heatmaps', 'month-chart');
				
			});
	});

	//week date selector at the right-chart field
   	$('input.datepicker').datetimepicker({
		format: 'L',
		defaultDate: new Date(),
    }).on('dp.change', function(ev){
    	new_date = new Date(ev.date);
    	var date = (new_date.getMonth() + 1) + '/' + new_date.getDate() + '/' + new_date.getFullYear();
    	$.get('/analytics/get_days_of_the_week_log', {date: date}).done(function(data){
    		charts.month_heatmap(data, '#bottom-right-chart-body', 'weekly-chart');
    	});

    });


	
});
