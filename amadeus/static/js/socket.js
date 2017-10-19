/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

if (("Notification" in window)) {
	if (Notification.permission !== 'denied') {
		Notification.requestPermission();
	}
}

var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
socket = new WebSocket(ws_scheme + "://" + window.location.host + "/");

socket.onmessage = function(e) {
	content = JSON.parse(e.data);

	if (content.type == "mural") {
		if (content.subtype == "post") {
			muralNotificationPost(content);
		} else if (content.subtype == "mural_update") {
			muralNotificationMuralUpdate(content);
		} else if (content.subtype == "mural_delete") {
			muralNotificationMuralDelete(content);
		} else if (content.subtype == "comment") {
			muralNotificationComment(content);
		}
	} else if (content.type == "chat") {
		messageReceived(content);
	} else if (content.type == "user_status") {
		changeUserStatus(content);
	}
}
// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();

function muralNotificationPost(content) {
	var page = window.location.pathname,
		render = (content.paths.indexOf(page) != -1),
		is_resource = (page.indexOf("resource") != -1);

	if ((render && page.indexOf(content.post_type) != -1) || (render && content.post_type == "general") || (render && is_resource)) {
		if (content.accordion) {
			var section = $(content.container);

			if (section.is(':visible')) {
				section.find('.posts').prepend(content.complete);

		        section.find('.no-subjects').hide();
		    }
		} else {
			$(content.container).prepend(content.complete);

	        $('.no-subjects').attr('style', 'display:none');
		}
	} else {
		$('.mural_badge').each(function () {
			var actual = $(this).text();

			if (actual != "+99") {
				actual = parseInt(actual, 10) + 1;

				if (actual > 99) {
					actual = "+99";
				}

				$(this).text(actual);
			}

			$(this).show();
		});

		$('.mural-tabs').find('li').each(function () {
			var identity = $(this).data('mural');

			if (identity == content.post_type) {
				var span = $(this).find('span'),
					actual = span.text();

				actual = parseInt(actual, 10) + 1;

				span.text(actual);
			}
		});

		if (content.post_type == "subjects") {
			var slug = content.container.substring(1, content.container.length),
				subject_mbadge = $("#subject_" + slug).find('.mural_notify'),
				actual = subject_mbadge.text();

			if (actual != "+99") {
				actual = parseInt(actual, 10) + 1;

				if (actual > 99) {
					actual = "+99";
				}

				subject_mbadge.text(actual);
			}

			subject_mbadge.show();
		}
	}

	if (("Notification" in window)) {
		var options = {
			icon: content.user_icon,
			body: content.simple_notify
		}

	    if (Notification.permission === "granted") {
	    	var notification = new Notification("", options);

	    	setTimeout(notification.close.bind(notification), 3000);
	    }
  	}
}

function muralNotificationMuralUpdate(content) {
	var page = window.location.pathname,
		render = (content.paths.indexOf(page) != -1);

	if (render) {
		var mural_item = $(content.container);

		if (mural_item.is(":visible") || mural_item.is(":hidden")) {
			mural_item.before(content.complete);

			mural_item.remove();
		}
	}
}

function muralNotificationMuralDelete(content) {
	var page = window.location.pathname,
		render = (content.paths.indexOf(page) != -1);

	if (render) {
		var mural_item = $(content.container);

		if (mural_item.is(":visible") || mural_item.is(":hidden")) {
			mural_item.remove();
		}
	}
}

function muralNotificationComment(content) {
	var page = window.location.pathname,
		render = (content.paths.indexOf(page) != -1),
		is_resource = (page.indexOf("resource") != -1),
		checker = "general";

	switch (content.post_type) {
		case "categorypost":
			checker = "categories";
			break;
		case "subjectpost":
			checker = "subjects";
			break;
	}

	if ((render && page.indexOf(checker) != -1) || (render && content.post_type == "generalpost" && page.indexOf("categories") == -1 && page.indexOf("subjects") == -1) || (render && is_resource)) {
		var section = $(content.container);

		if (section.is(":visible") || section.is(":hidden")) {
			var comments = section.find('.comment-section');

			comments.append(content.complete);
		}
	} else {
		$('.mural_badge').each(function () {
			var actual = $(this).text();

			if (actual != "+99") {
				actual = parseInt(actual, 10) + 1;

				if (actual > 99) {
					actual = "+99";
				}

				$(this).text(actual);
			}

			$(this).show();
		});

		$('.mural-tabs').find('li').each(function () {
			var identity = $(this).data('mural');

			if ((identity == checker) || (identity == "general" && content.post_type == "generalpost")) {
				var span = $(this).find('span'),
					actual = span.text();

				actual = parseInt(actual, 10) + 1;

				span.text(actual);
			}
		});

		if (content.post_type == "subjectpost") {
			var subject_mbadge = $("#subject_" + content.type_slug).find('.mural_notify'),
				actual = subject_mbadge.text();

			if (actual != "+99") {
				actual = parseInt(actual, 10) + 1;

				if (actual > 99) {
					actual = "+99";
				}

				subject_mbadge.text(actual);
			}

			subject_mbadge.show();
		}
	}

	if (("Notification" in window)) {
		var options = {
			icon: content.user_icon,
			body: content.simple_notify
		}

	    if (Notification.permission === "granted") {
	    	var notification = new Notification("", options);

	    	setTimeout(notification.close.bind(notification), 3000);
	    }
  	}
}

function messageReceived(content) {
	var talk_modal = $("#" + content.container);

	if (talk_modal.is(':visible')) {
		var new_msg_btn = talk_modal.find('.messages_new'),
			msg_container = talk_modal.find('.messages-container');

		talk_modal.find('.messages-list').append(content.complete);

		new_msg_btn.show();

		new_msg_btn.click(function () {
			var height = msg_container[0].scrollHeight;

            msg_container.animate({scrollTop: height}, 0);

            $(this).hide();
		});

		$.ajax({
			type: 'GET',
			url: content.view_url
		});
	} else {
		var talk_line = $("#talk-" + content.container),
			talk_notifies = talk_line.find('.chat_notify_list'),
			actual_count = talk_notifies.text(),
			actual_date = talk_line.find(".talk-last_msg");

			actual_count = parseInt(actual_count, 10) + 1;

			talk_notifies.text(actual_count);

			actual_date.html(content.last_date);

		$('.chat_badge').each(function () {
			var actual = $(this).text();

			if (actual != "+99") {
				actual = parseInt(actual, 10) + 1;

				if (actual > 99) {
					actual = "+99";
				}

				$(this).text(actual);
			}

			$(this).show();
		});

		if (content.subtype == "subject") {
			var subject_cbadge = $("#subject_" + content.space).find('.chat_notify'),
				actual = subject_cbadge.text();

			if (actual != "+99") {
				actual = parseInt(actual, 10) + 1;

				if (actual > 99) {
					actual = "+99";
				}

				subject_cbadge.text(actual);
			}

			subject_cbadge.show();
		}
	}

	if (("Notification" in window)) {
		var options = {
			icon: content.user_icon,
			body: content.simple_notify
		}

	    if (Notification.permission === "granted") {
	    	var notification = new Notification(content.notify_title, options);

	    	setTimeout(notification.close.bind(notification), 3000);
	    }
  	}
}

function changeUserStatus(content) {
	var elem = $(".user_" + content.user_id + "_status");

	elem.removeClass(content.remove_class);

	if (content.status_class == "") {
		elem.removeClass('active');
	} else {
		elem.addClass(content.status_class);
	}

	elem.attr('data-original-title', content.status);
}
