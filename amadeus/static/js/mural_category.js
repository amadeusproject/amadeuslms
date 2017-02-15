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
			loading = $(this).find('.loading-posts'),
			more = $(this).find('.more-posts'),
			filters = $(this).find('.post-filters'),
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

                    	without.hide();
                    } else {
                    	more.hide();

                    	without.show();
                    }
                }
            });
		}

		more.click(function () {
			var url = mural.data('url'),
				pageNum = mural.data('page'),
		        numberPages = mural.data('pages'),
		        favorites = mural.data('fav'),
		        mine = mural.data('mine'),
		        showing = new_posts.join(',');

		    if (pageNum == numberPages) {
		        return false
		    }

		    pageNum = pageNum + 1;

		    more.hide();

		    loading.show();

		    $.ajax({
		    	url: url,
		    	data: {'page': pageNum, 'favorite': favorites, 'mine': mine, 'showing': showing},
		    	dataType: 'json',
		    	success: function (data) {
		    		loading.hide();

		    		post_section.append(data.posts);

                	mural.data('pages', data.num_pages);
                	mural.data('page', data.num_page);

                	setTimeout(function () { postHeightLimits() }, 100);

                	if (data.num_page < data.num_pages) {
                		more.show();
                	} else {
                		more.hide();
                	}
		    	}
		    });
		});

		filters.submit(function () {
			var favorite = $(this).find("input[name='favorite']").is(':checked') ? "True" : "",
				mine = $(this).find("input[name='mine']").is(':checked') ? "True" : "",
				url = mural.data('url');

			post_section.html('');

			more.hide();
			loading.show();

			$.ajax({
				url: url,
				data: {'favorite': favorite, 'mine': mine},
				dataType: 'json',
				success: function (data) {
					loading.hide();

					if (data.count > 0) {
                    	post_section.append(data.posts);

                    	mural.data('pages', data.num_pages);
                    	mural.data('page', data.num_page);

                    	if (data.num_page < data.num_pages) {
                    		more.show();
                    	} else {
                    		more.hide();
                    	}

                    	setTimeout(function () { postHeightLimits() }, 100);

                    	without.hide();
                    } else {
                    	without.show();
                    }

                    mural.data('fav', favorite);
                    mural.data('mine', mine);
				}
			});

			return false;
		});
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