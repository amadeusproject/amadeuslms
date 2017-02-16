$('.mural-subject').on('shown.bs.collapse', function(e) {
    if($(this).is(e.target)){
    	var li = $(".breadcrumb").find('li:last-child');
		var li_text = $(li).html();
		var url = $(".mural_url").val();
		var new_li = $(li).clone();
		
		new_li.html($(this).parent().find('.panel-title span').text());

		$(li).html("<a href='" + url + "'>" + li_text + "</a>");
		$(li).append("<span class='divider'>/</span>");

		new_li.appendTo('.breadcrumb');
	}
});

$('.mural-subject').on('hidden.bs.collapse', function(e) {
    if($(this).is(e.target)){
    	$(".breadcrumb").find('li:last-child').remove();

		var li = $(".breadcrumb").find('li:last-child');
		var text = $(li).find('a').text();

		$(li).html(text);
    }
});