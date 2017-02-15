if (("Notification" in window)) {
	if (Notification.permission !== 'denied') {
		Notification.requestPermission();
	}
}

socket = new WebSocket("ws://" + window.location.host + "/");

socket.onmessage = function(e) {
	content = JSON.parse(e.data);

	if (content.type == "mural") {
		if (content.subtype == "create") {
			muralNotificationCreate(content);
		} else if (content.subtype == "update") {
			muralNotificationUpdate(content);
		} else if (content.subtype == "delete") {
			muralNotificationDelete(content);
		} else if (content.subtype == "create_comment") {
			muralNotificationComment(content);
		} else if (content.subtype == "update_comment") {
			muralNotificationCommentUpdate(content);
		} else if (content.subtype == "delete_comment") {
			muralNotificationCommentDelete(content);
		} else if (content.subtype == "create_cat") {
			muralNotificationCategory(content);
		} else if (content.subtype == "update_cat") {
			muralNotificationCategoryUpdate(content);
		} else if (content.subtype == "delete_cat") {
			muralNotificationCategoryDelete(content);
		}
	}
}
// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();

function muralNotificationCreate(content) {
	if (window.location.pathname == content.pathname) {
		$('.posts').prepend(content.complete);

        $('.no-subjects').attr('style', 'display:none');
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
			body: content.simple
		}

	    if (Notification.permission === "granted") {
	    	var notification = new Notification("", options);

	    	setTimeout(notification.close.bind(notification), 3000);
	    }
  	}
}

function muralNotificationUpdate(content) {
	if (window.location.pathname == content.pathname) {
		var post = $("#post-" + content.post_id);

		if (post.is(":visible")) {
			post.before(content.complete);

			post.remove();
		}
	}
}

function muralNotificationDelete(content) {
	if (window.location.pathname == content.pathname) {
		var post = $("#post-" + content.post_id);

		if (post.is(":visible")) {
			post.remove();
		}
	}
}

function muralNotificationComment(content) {
	if (window.location.pathname == content.pathname) {
		if ($("#post-" + content.post_id).is(":visible")) {
			var section = $("#post-" + content.post_id).find('.comment-section');

			section.append(content.complete);
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
			body: content.simple
		}

	    if (Notification.permission === "granted") {
	    	var notification = new Notification("", options);

	    	setTimeout(notification.close.bind(notification), 3000);
	    }
  	}
}

function muralNotificationCommentUpdate(content) {
	if (window.location.pathname == content.pathname) {
		var comment = $("#comment-" + content.comment_id);

		if (comment.is(":visible")) {
			comment.before(content.complete);

			comment.remove();
		}
	}
}

function muralNotificationCommentDelete(content) {
	if (window.location.pathname == content.pathname) {
		var comment = $("#comment-" + content.comment_id);

		if (comment.is(":visible")) {
			comment.remove();
		}
	}
}

function muralNotificationCategory(content) {
	var cat_section = $("#" + content.cat);
	
	if (window.location.pathname == content.pathname && cat_section.is(':visible')) {
		
		cat_section.find('.posts').prepend(content.complete);

        cat_section.find('.no-subjects').hide();
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
			body: content.simple
		}

	    if (Notification.permission === "granted") {
	    	var notification = new Notification("", options);

	    	setTimeout(notification.close.bind(notification), 3000);
	    }
  	}
}

function muralNotificationCategoryUpdate(content) {
	if (window.location.pathname == content.pathname) {
		var post = $("#post-" + content.post_id);

		if (post.is(":visible") || post.is(":hidden")) {
			post.before(content.complete);

			post.remove();
		}
	}
}

function muralNotificationCategoryDelete(content) {
	if (window.location.pathname == content.pathname) {
		var post = $("#post-" + content.post_id);

		if (post.is(":visible") || post.is(":hidden")) {
			post.remove();
		}
	}
}