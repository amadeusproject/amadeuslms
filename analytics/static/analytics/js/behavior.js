
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
			if (e.attributes['data-url'].value == "subjects"){
				var url = "/analytics/most_accessed_subjects";
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
		string_build += "<ul>";
		
		data.forEach(function(datum){
			string_build += '<li class="most-accessed-item">' +datum.name+ ' ' + datum.count+ '</li>';
		});
		string_build += "</ul>";
		
		$(e).append(string_build);

		e.attributes.open = True;
		
	},
};
