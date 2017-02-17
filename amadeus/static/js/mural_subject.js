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

		var post_section = $(this).find('.posts'),
			without = $(this).find('.no-subjects'),
			loading = $(this).find('.loading-posts'),
			more = $(this).find('.more-posts'),
			filters = $(this).find('.post-filters'),
			clear_filters = $(this).find('.clear_filter'),
			mural = post_section.parent().parent();

		if (post_section.children().length == 0) {
			var url = $(this).find('.mural').data('url');

			$.ajax({
                url: url,
                dataType: 'json',
                success: function (data) {
                	loading.hide();

                    if (data.count > 0) {
                    	post_section.append(data.posts);

                    	mural.data('pages', data.num_pages);
                    	mural.data('page', data.num_page);

                    	setTimeout(function () { postHeightLimits() }, 100);

                    	if (data.num_page < data.num_pages) {
                    		more.show();
                    	} else {
                    		more.hide();
                    	}

                    	$('.mural_badge').each(function () {
							var actual = $(this).text();

							if (actual != "+99") {
								actual = parseInt(actual, 10) - data.unviewed;

								if (actual <= 0) {
									$(this).hide();
								} else {
									$(this).text(actual);
								}
							}
						});

						$('.sub_badge').each(function () {
							var actual = $(this).text();

							if (actual != "+99") {
								actual = parseInt(actual, 10) - data.unviewed;

								if (actual < 0) {
									actual = 0;
								}
								
								$(this).text(actual);
							}
						});

                    	without.hide();
                    } else {
                    	more.hide();

                    	without.show();
                    }
                }
            });
		}
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