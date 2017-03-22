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

                setShortChatFormSubmit();
            });

            $("#msg_editable").on('click', function () {
                $(this).trigger('focusin');
            });

            $("#msg_editable").on('focusin', function () {
                $("#send-img").hide();
                $("#send-msg").show();

                $(".msg_placeholder").hide();
            });

            $("#msg_editable").on('focusout', function (event) {
                if (!$(event.relatedTarget).is("#send-msg")) {
                    $("#send-img").show();
                    $("#send-msg").hide();

                    var content = $(this).html();

                    if (content == "") {
                        $(".msg_placeholder").show();     
                    }
                }
            });

            $("#msg_editable").on('keydown', function (e) {
                if (e.keyCode == 13 && !e.shiftKey) {
                    e.preventDefault();

                    $("#short-chat").submit();
                }
            });
		}
	});
}

function getForm(field) {
    var url = field.data('url');

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

function setShortChatFormSubmit() {
    var frm = $('#short-chat'),
        editable = $("#msg_editable");

    frm.submit(function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        if (editable.html() != "") {
            $("#id_text").val("<p>" + editable.html() + "</p>");
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

                    editable.html("");
                    editable.trigger("focusout");

                    alertify.success(data.message);
                },
                error: function(data) {
                    alertify.error(data.responseText);
                    setShortChatFormSubmit();
                },
                cache: false,
                contentType: false,
                processData: false
            });
        }

        return false;
    });
}