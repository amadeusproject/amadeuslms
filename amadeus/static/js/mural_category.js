$('.mural-category').on('shown.bs.collapse', function(e) {
    if($(this).is(e.target)){
    	var li = $(".breadcrumb").find('li:last-child');
		var li_text = $(li).html();
		var url = $(".mural_url").val();
		var new_li = $(li).clone();
		
		new_li.html($(this).parent().find('.panel-title span').text());

		$(li).html("<a href='" + url + "'>" + li_text + "</a>");
		$(li).append("<span class='divider'>/</span>");

		new_li.appendTo('.breadcrumb');

		var post_section = $(this).find('.posts'),
			without = $(this).find('.no-subjects'),
			loading = $(this).find('.loading-posts');

		if (post_section.children().length == 0) {
			var url = $(this).find('.mural').data('url');

			$.ajax({
                url: url,
                dataType: 'json',
                success: function (data) {
                	loading.hide();

                    if (data.count > 0) {
                    	post_section.append(data.posts);

                    	without.hide();
                    } else {
                    	without.show();
                    }
                }
            });
		}
    }
});

$('.mural-category').on('hidden.bs.collapse', function(e) {
    if($(this).is(e.target)){
    	$(".breadcrumb").find('li:last-child').remove();

		var li = $(".breadcrumb").find('li:last-child');
		var text = $(li).find('a').text();

		$(li).html(text);
    }
});