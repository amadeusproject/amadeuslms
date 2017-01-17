$('.collapse').on('shown.bs.collapse', function (e) {
    if($(this).is(e.target)){
    	var li = $(".breadcrumb").find('li:last-child');
    	var li_text = $(li).html();
    	var url = $(".subs_url").val();
    	var new_li = $(li).clone();
    	
    	new_li.html($(this).parent().find('.panel-title').text());

    	$(li).html("<a href='" + url + "'>" + li_text + "</a>");
    	$(li).append("<span class='divider'>/</span>");

    	new_li.appendTo('.breadcrumb');
    }
});

$('.collapse').on('hide.bs.collapse', function (e) {
    if($(this).is(e.target)){
    	$(".breadcrumb").find('li:last-child').remove();

    	var li = $(".breadcrumb").find('li:last-child');
    	var text = $(li).find('a').text();

    	$(li).html(text);
	}
});

// utilizado para fazer a re-organização dos tópicos
$("#topics-accordion").sortable({ 
    delay: 100,
    distance: 5,
    handler: 'i.fa-arrows',
    update: function( event, ui ) {
  		var cont = 1;
  		var data = [];
  		
  		$("#topics-accordion").find('.order_inp').each(function () {
  			$(this).val(cont++);

  			data.push({
  				'topic_id': $(this).parent().find('.id_inp').val(),
  				'topic_order': $(this).val()
  			});
  		});

  		data = JSON.stringify(data);

  		sendUpdate(data);
    },
});

function sendUpdate(data) {
	$.ajax({
		url: $('.url_order').val(),
		dataType: 'json',
		data: {'data': data},
		success: function(response) {
			console.log(response);
		},
		error: function(response) {
			console.log(response);	
		}
	});
}