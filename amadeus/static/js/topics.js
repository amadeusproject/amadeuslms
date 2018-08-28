/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

$('.topic-panel').on('show.bs.collapse', function (e) {
	if($(this).is(e.target)){
		var btn = $(this).parent().find('.fa-angle-right');

		btn = btn[0];
		
		$(btn).switchClass("fa-angle-right", "fa-angle-down", 250, "easeInOutQuad");

		var url = $(this).parent().find('.log_url').val();
        var log_input = $(this).parent().find('.log_id');

        if (typeof(url) != 'undefined') {
            $.ajax({
                url: url,
                data: {'action': 'open'},
                dataType: 'json',
                success: function (data) {
                    log_input.val(data.log_id);
                },
                error: function (data) {
                    console.log(data);
                }
            });
        }

		$(this).parent().parent().find('.panel-collapse.in').collapse('hide');
	}
});

// Update breadcrumb with topic's name
$('.topic-panel').on('shown.bs.collapse', function (e) {
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
$('.topic-panel').on('hide.bs.collapse', function (e) {
	if($(this).is(e.target)){
		var btn = $(this).parent().find('.fa-angle-down');
			
		btn = btn[0];
		
		$(btn).switchClass("fa-angle-down", "fa-angle-right", 250, "easeInOutQuad");

		$(".breadcrumb").find('li:last-child').remove();

		var li = $(".breadcrumb").find('li:last-child');
		var text = $(li).find('a').text();

		$(li).html(text);

		var url = $(this).parent().find('.log_url').val();
        var log_id = $(this).parent().find('.log_id').val();

        if (typeof(url) != 'undefined') {
            $.ajax({
                url: url,
                data: {'action': 'close', 'log_id': log_id},
                dataType: 'json',
                success: function (data) {
                    console.log(data.message);
                },
                error: function (data) {
                    console.log(data);
                }
            });
        }
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