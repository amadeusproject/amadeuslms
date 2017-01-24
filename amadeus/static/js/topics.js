// Update breadcrumb with topic's name
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

// Reset breadcrumb to it's normal state
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
    handle: 'i.move_topic',
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

function delete_topic(url) {
	$('.modal').remove();

	$.get(url, function (modal) {
		$("#topics-accordion").after(modal);

		$('.modal').modal('show');
	});
}

$(".add_resource").on('show.bs.dropdown', function () {
    $(this).find('i.fa-angle-right').switchClass("fa-angle-right", "fa-angle-down", 250, "easeInOutQuad");
});

$(".add_resource").on('hide.bs.dropdown', function () {
    $(this).find('i.fa-angle-down').switchClass("fa-angle-down", "fa-angle-right", 250, "easeInOutQuad");
});