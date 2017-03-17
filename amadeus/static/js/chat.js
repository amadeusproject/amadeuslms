function getModalInfo(btn, space, space_type) {
	var url = btn.data('url');

	$.ajax({
		method: 'get',
		url: url,
		data: {'space': space, 'space_type': space_type},
		success: function (response) {
			$("#chat-modal-info").html(response);

			$("#chat-modal-info").modal('show');

			$.material.init();

            $('#chat-modal-info').on('shown.bs.modal', function () {
                $(".messages-container").each(function () {
                    var height = $(this)[0].scrollHeight;

                    $(this).animate({scrollTop: height}, 0);
                });
            });
		}
	});
}

function getForm(field) {
    var url = field.find('h4').data('url');

    $.ajax({
        url: url,
        success: function (data) {
            $('#chat-modal-form').html(data);

            setChatFormSubmit();

            $('#chat-modal-form').modal('show');
        }
    });
}

function setChatFormSubmit() {
    var frm = $('#chat-form');

    frm.submit(function () {
        var formData = new FormData($(this)[0]);

        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: formData,
            dataType: "json",
            async: false,
            success: function (data) {
                $('.messages-list').append(data.view);

                $(".messages-container").each(function () {
                    var height = $(this)[0].scrollHeight;

                    $(this).animate({scrollTop: height}, 0);
                });

                $('#chat-modal-form').modal('hide');

                alertify.success(data.message);
            },
            error: function(data) {
                $("#chat-modal-form").html(data.responseText);
                setChatFormSubmit();
            },
            cache: false,
            contentType: false,
            processData: false
        });

        return false;
    });
}