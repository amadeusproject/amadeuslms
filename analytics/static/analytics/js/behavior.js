
$(document).ready(function(){
	selectors_options.init();
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
			if (typeof opened !== typeof undefined && opened !== false){
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
		new_elem.slideDown();
		$(e).attr("opened", true);
		
	},
	deleteChildren: function(e){
		console.log("delete children");
		var most_accessed_list = $(e).next();
		$(most_accessed_list).animate(
			{height: 0,
			 opacity: 0.1
			}, 1000, function(){
			$(this).remove(); //remove list from UI
		});
		
		$(e).removeAttr("opened"); //remove attribute so it can call API again
	},
};
