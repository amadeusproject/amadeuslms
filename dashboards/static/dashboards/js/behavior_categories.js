$(document).ready(function(){
	charts.most_used_tags('/analytics/get_category_tags/?category_id='+$("#category-selector").val());
	
	$("#category-selector").on("change", function(e){
		//when it changes, the tag chart is replaced and all others are.
		category_id = $(e.target).val();
		charts.most_used_tags('/analytics/get_category_tags/?category_id='+category_id);
	});
});

