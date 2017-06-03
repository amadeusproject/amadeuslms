


$(document).ready(function(){
	selectors_options.init();

	charts.most_used_tags('/analytics/most_used_tags');
	charts.build_bubble_user('/analytics/most_active_users/');
	

	$('#month_selector').change(function(){

		var date = $(this).val().split("/");
		$.get('/analytics/amount_active_users_per_day', {month: date[0], year: date[1] }).done(function(data){
			charts.month_heatmap(data, '#right-chart-body', 'month-chart');
			
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
 	$.get('/analytics/amount_active_users_per_day', { month: month[(new Date()).getMonth()] }).done(function(data){
			charts.month_heatmap(data, '#right-chart-body', 'month-chart');
	});

 	//first call to weekly chart
 	var today_date = new Date();
 	var date = (today_date.getMonth() + 1) + '/' + today_date.getDate() + '/' + today_date.getFullYear();
 	$.get('/analytics/get_days_of_the_week_log', {date: date}).done(function(data){
    		charts.month_heatmap(data, '#bottom-right-chart-body', 'weekly-chart');
    });



});



var selectors_options = {
	init: function(){
		selectors = $("div.selector");
		selectors.click(function(e){
			selectors_options.loadData(e.currentTarget);
		});
	},
	loadData: function(e){
		if (e){
			opened = $(e).attr('opened');
			if (opened == "true"){
				selectors_options.deleteChildren(e);
			}else {
				switch(e.attributes['data-url'].value){
					case "subjects":
						var url = "/analytics/most_accessed_subjects";
						break;
					case "categories":
						var url = "/analytics/most_accessed_categories";
						break;
					case "resources":
						var url = "/analytics/most_accessed_resources";
						break;

				}	
			
			}
		}
		if(url){
			$.get(url, function(dataset){
				return dataset;
			}).done(function(data){
				selectors_options.modifyElement(e, data);
				
			}).fail(function(error){
				console.log("couldn't complete get request");
			});
		}
	
		
	},
	modifyElement: function(e, data){
		var string_build = "";
		string_build += '<ul class="most-accessed-list" style="display:none;">';
		
		data.forEach(function(datum){
			string_build += '<li class="most-accessed-item">' +datum.name+ ' ' + datum.count+ '</li>';
		});
		string_build += "</ul>";
		
		$(e).after(string_build);
		var new_elem = $(e).next();
		$(new_elem).addClass($(e).attr("data-url"));
		new_elem.slideDown({easing: 'easeInOutSine'}, 5000);
		$(e).attr("opened", true);
		
	},
	deleteChildren: function(e){
		var most_accessed_list = $(e).siblings("." + $(e).attr("data-url"));
		$(most_accessed_list).slideUp({easing: 'easeInOutSine'}, 1200);
		$(most_accessed_list).remove();
		$(e).attr("opened", false); //remove attribute so it can call API again
	},
};


