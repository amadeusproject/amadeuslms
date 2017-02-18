if (("Notification" in window)) {
	if (Notification.permission !== 'denied') {
		Notification.requestPermission();
	}
}

socket = new WebSocket("ws://" + window.location.host + "/");

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
	}
}
// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();

function muralNotificationPost(content) {
	var page = window.location.pathname,
		render = (content.paths.indexOf(page) != -1);

	if (render) {
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
		checker = "";

	switch (content.post_type) {
		case "categorypost":
			checker = "category";
			break;
		case "subjectpost":
			checker = "subject";
			break;
	}

	if ((render && page.indexOf(checker) != -1) || (render && content.post_type == "generalpost")) {
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