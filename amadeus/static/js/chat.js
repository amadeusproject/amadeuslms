function getModalInfo(btn, space) {
	var url = btn.data('url');

	$.ajax({
		method: 'get',
		url: url,
		data: {'space': space},
		success: function (response) {
			$("#chat-modal-info").html(response);

			$("#chat-modal-info").modal('show');

			$.material.init();
		}
	});
}