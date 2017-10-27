/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

$('.mural-ungeneral').on('shown.bs.collapse', function(e) {
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

                    	setUserDataPopover();
                    	setTimeout(function () { postHeightLimits(); }, 100);

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
									$(this).text("0");
									$(this).hide();
								} else {
									$(this).text(actual);
								}
							}
						});

						$('.ung_badge').each(function () {
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

                	setUserDataPopover();
                	setTimeout(function () { postHeightLimits(); }, 100);

                	if (data.num_page < data.num_pages) {
                		more.show();
                	} else {
                		more.hide();
                	}
		    	}
		    });
		});

		$("input[name='favorite']").on('click', function () {
			var checked = $(this).is(':checked');

			$("input[name='favorite']").each(function () {
				$(this).prop('checked', checked);
			});
		});

		$("input[name='mine']").on('click', function () {
			var checked = $(this).is(':checked');

			$("input[name='mine']").each(function () {
				$(this).prop('checked', checked);
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

                    	setUserDataPopover();
                    	setTimeout(function () { postHeightLimits(); }, 100);

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

		var favorite = filters.find("input[name='favorite']"),
	        mine = filters.find("input[name='mine']");

	    favorite.on('change', function () {
	        filters.submit();
	    });

	    mine.on('change', function () {
	        filters.submit();
	    });

		clear_filters.click(function () {
	        var frm = $(this).parent();

	        $("input[type='checkbox']").prop('checked', false);

	        frm.submit();
	    });
    }
});

$('.mural-ungeneral').on('hidden.bs.collapse', function(e) {
    if($(this).is(e.target)){
    	$(".breadcrumb").find('li:last-child').remove();

		var li = $(".breadcrumb").find('li:last-child');
		var text = $(li).find('a').text();

		$(li).html(text);
    }
});