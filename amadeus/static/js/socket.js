if (("Notification" in window)) {
	if (Notification.permission !== 'denied') {
		Notification.requestPermission();
	}
}


socket = new WebSocket("ws://" + window.location.host + "/");

socket.onmessage = function(e) {
	content = JSON.parse(e.data);

	if (content.type == "mural") {
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
}
// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();