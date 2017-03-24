var new_msgs = {};

$('#chat-modal-info').on('show.bs.modal', function (e) {
    var header = $(this).find('.talk_header');
    if (header.length > 0) {
        var li = $(".breadcrumb").find('li:last-child');
        var li_text = $(li).html();
        var new_li = $(li).clone();
        
        new_li.html(header.find('h4').data('breadcrumb'));

        $(li).html("<a href='#'>" + li_text + "</a>");
        $(li).append("<span class='divider'>/</span>");

        new_li.appendTo('.breadcrumb');
    }
});

$('#chat-modal-info').on('hide.bs.modal', function (e) {
    var header = $(this).find('.talk_header');
    if (header.length > 0) {
        $(".breadcrumb").find('li:last-child').remove();

        var li = $(".breadcrumb").find('li:last-child');
        var text = $(li).find('a').text();

        $(li).html(text);
    }
});


function getModalInfo(btn, space, space_type) {
	var url = btn.data('url');

	$.ajax({
		method: 'get',
		url: url,
		data: {'space': space, 'space_type': space_type},
		success: function (response) {
            var modal_shown = $("#chat-modal-info").is(":visible");

			$("#chat-modal-info").html(response);

			$("#chat-modal-info").modal('show');

			$.material.init();

            if (modal_shown) {
                $(".messages-container").each(function () {
                    var height = $(this)[0].scrollHeight;

                    $(this).animate({scrollTop: height}, 0);
                });

                setShortChatFormSubmit();
                setFiltersSubmitAndPagination();
            } else {
                $('#chat-modal-info').on('shown.bs.modal', function () {
                    $(".messages-container").each(function () {
                        var height = $(this)[0].scrollHeight;

                        $(this).animate({scrollTop: height}, 0);
                    });

                    setShortChatFormSubmit();
                    setFiltersSubmitAndPagination();
                });
            }

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

                if (typeof(new_msgs[data.talk_id]) == 'undefined') {
                    new_msgs[data.talk_id] = [];
                }

                new_msgs[data.talk_id].push(data.new_id);

                $('#chat-modal-form').modal('hide');
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

                    if (typeof(new_msgs[data.talk_id]) == 'undefined') {
                        new_msgs[data.talk_id] = [];
                    }

                    new_msgs[data.talk_id].push(data.new_id);

                    editable.html("");
                    editable.trigger("focusout");
                },
                error: function(data) {
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

function favorite(btn) {
    var action = btn.data('action'),
        url = btn.data('url');

    $.ajax({
        url: url,
        data: {'action': action},
        dataType: 'json',
        success: function (response) {
            if (action == 'favorite') {
                btn.switchClass("btn_fav", "btn_unfav", 250, "easeInOutQuad");
                btn.data('action', 'unfavorite');
            } else {
                btn.switchClass("btn_unfav", "btn_fav", 250, "easeInOutQuad");
                btn.data('action', 'favorite');
            }

            btn.attr('data-original-title', response.label);
        }
    });
}

function setFiltersSubmitAndPagination() {
    var filters = $('#chat-filters'),
        clear_filters = $('#clear_filter'),
        messages = $('.messages-container'),
        loading = messages.find('.loading-msgs'),
        more = messages.find('.more-msgs'),
        msg_section = $('.messages-list');

    filters.submit(function () {
        var favorite = $(this).find("input[name='favorite']").is(':checked') ? "True" : "",
            mine = $(this).find("input[name='mine']").is(':checked') ? "True" : "",
            url = messages.data('url');

        msg_section.html('');

        more.hide();
        loading.show();

        $.ajax({
            url: url,
            data: {'favorite': favorite, 'mine': mine},
            dataType: 'json',
            success: function (data) {
                loading.hide();

                if (data.count > 0) {
                    msg_section.append(data.messages);

                    messages.data('pages', data.num_pages);
                    messages.data('page', data.num_page);

                    if (data.num_page < data.num_pages) {
                        more.show();
                    } else {
                        more.hide();
                    }
                }

                messages.data('fav', favorite);
                messages.data('mine', mine);

                messages.each(function () {
                    var height = $(this)[0].scrollHeight;

                    $(this).animate({scrollTop: height}, 0);
                });
            }
        });

        return false;
    });

    clear_filters.click(function () {
        var frm = $(this).parent();

        $("input[type='checkbox']").prop('checked', false);

        frm.submit();
    });

    more.click(function () {
        var url = messages.data('url'),
            pageNum = messages.data('page'),
            numberPages = messages.data('pages'),
            favorites = messages.data('fav'),
            mine = messages.data('mine'),
            talk = messages.data('talk');

        var showing;

        if (typeof(new_msgs[talk]) == 'undefined') {
            showing = "";
        } else {
            showing = new_msgs[talk].join(',');
        }

        if (pageNum == numberPages) {
            return false
        }

        pageNum = pageNum + 1;

        more.hide();
        loading.show();

        $.ajax({
            url: url,
            data: {'page': pageNum, 'favorite': favorites, 'mine': mine, 'showing': showing},
            dataType: 'json',
            success: function (data) {
                loading.hide();

                msg_section.prepend(data.messages);

                messages.data('pages', data.num_pages);
                messages.data('page', data.num_page);

                if (data.num_page < data.num_pages) {
                    more.show();
                } else {
                    more.hide();
                }
            }
        });
    });
}