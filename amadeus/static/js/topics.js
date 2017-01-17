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