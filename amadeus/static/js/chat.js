var new_msgs = {};

$(document).on('hidden.bs.modal', '.modal', function () {
    $('.modal:visible').length && $(document.body).addClass('modal-open'); //Fixing scroll bar for modals
});

$(document).on("click", function (e) {
    //console.log(e);
    var container = $('#participants'),
        $popover = $('.popover'),
        list = container.parent().find(".participants-list");;

    if (!container.is(e.target) && container.has(e.target).length === 0 
        && !list.is(e.target) && list.has(e.target).length === 0
        && !$popover.is(e.target) && $popover.has(e.target).length === 0) {
        if (container.hasClass('open')) {
            container.animate({
                right : '0px'
            }, 500);

            list.animate({
                right : '-180px',
                opacity: 0
            }, 500).css({display: "none", visibility: 'hidden'});

            container.removeClass('open');
        }
    }
});

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

                $(".messages-container").on('scroll', function () {
                    if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
                        $('.messages_new').hide();
                    }
                });

                setShortChatFormSubmit();
                setFiltersSubmitAndPagination();
            } else {
                $('#chat-modal-info').on('shown.bs.modal', function () {
                    $(".messages-container").each(function () {
                        var height = $(this)[0].scrollHeight;

                        $(this).animate({scrollTop: height}, 0);
                    });

                    $(".messages-container").on('scroll', function () {
                        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
                            $('.messages_new').hide();
                        }
                    });

                    var viewed = $(".messages-container").data('viewed'),
                        sub_badge = $(".messages-container").data('space'),
                        father = $(".messages-container").parent().parent().parent().parent(),
                        chat_list_item_id = "#talk-" + father.attr("id");

                    $('.chat_badge').each(function () {
                        var actual = $(this).text();

                        if (actual != "+99") {
                            actual = parseInt(actual, 10) - viewed;

                            if (actual <= 0) {
                                $(this).text("0");
                                $(this).hide();
                            } else {
                                $(this).text(actual);
                            }
                        }
                    });

                    var counter = $(chat_list_item_id).find('.chat_notify_list').text();

                    counter = parseInt(counter, 10) - viewed;

                    if (counter <= 0) {
                        counter = "0";
                    }

                    $(chat_list_item_id).find('.chat_notify_list').text(counter);

                    var subject_cbadge = $("#subject_" + sub_badge).find('.chat_notify'),
                        actual = subject_cbadge.text();

                    if (actual != "+99") {
                        actual = parseInt(actual, 10) - viewed;

                        if (actual <= 0) {
                            subject_cbadge.text("0");
                            subject_cbadge.hide();
                        }
                    }

                    setShortChatFormSubmit();
                    setFiltersSubmitAndPagination();
                });
            }

            $("#msg_editable").on('click', function () {
                $(this).trigger('focusin');
            });

            $("#msg_editable").on('focusin', function () {
                $(".msg_placeholder").hide();                
            });

            $("#msg_editable").on('keydown', function () {
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
    var frm = $('#chat-form'),
        error_msg = frm.data('error');

    frm.submit(function (e) {
        var btn = frm.parent().parent().find("button[form='chat-form']");

        btn.prop('disable', true);
        btn.prop('disabled', true);

        var formData = new FormData($(this)[0]),
            file = $("#id_image")[0].files[0],
            max_filesize = 5*1024*1024;

        if (typeof(file) != "undefined") {
            var image_container = $("#id_image").parent(),
                overlay_msg = image_container.data('overlay'),
                wrong_format_msg = image_container.data('invalid'),
                file_type = file.type,
                type_accept = /^image\/(jpg|png|jpeg|gif)$/;

            if (file.size > max_filesize) {
                image_container.append('<div class="alert alert-danger alert-dismissible" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><ul><li>' + overlay_msg + '</li></ul></div>');

                return false;
            }

            if (!type_accept.test(file_type)) {
                image_container.append('<div class="alert alert-danger alert-dismissible" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><ul><li>' + wrong_format_msg + '</li></ul></div>');

                return false;   
            }
        }

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

                frm.attr('action', data.new_form_url);
                $("#short-chat").attr('action', data.new_form_url);
                $("#send-img").data('url', data.new_form_url);

                $('#chat-modal-form').modal('hide');
            },
            error: function(data) {
                if (data.status == 400) {
                    $("#chat-modal-form").html(data.responseText);
                } else {
                    alertify.error(error_msg);
                }

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
                    editable.blur();

                    frm.attr('action', data.new_form_url);
                    $("#send-img").data('url', data.new_form_url);
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
                    msg_section.html(data.messages);

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

function getParticipants(btn) {
    var url = btn.attr('href'),
        container = btn.parent().parent().parent().parent(),
        content_section = container.find('.content');

    $.ajax({
        url: url,
        success: function (response) {
            content_section.html(response);

            var items = $('#content-list').children(":visible").length;
            var holder = content_section.find('.holder');

            if (items > 10) {
                holder.jPages({
                    containerID : "content-list",
                    perPage: 10,
                    previous: "«",
                    next: "»",
                    midRange: 5
                });
            }

            var li = $(".breadcrumb").find('li:last-child'),
                li_text = $(li).html(),
                new_li_text = container.data('breadtext');

            if (li_text == new_li_text) {

                $(".breadcrumb").find('li:last-child').remove();
            }

            var new_li = $(li).clone();
                        
            new_li.html(new_li_text);

            $(li).html("<a href='" + container.data('breadurl') + "'>" + li_text + "</a>");
            $(li).append("<span class='divider'>/</span>");

            new_li.appendTo('.breadcrumb');
        }
    });
}

function setSearchSubmit() {
    var frm = $("#search-participants"),
        container = frm.parent().parent().parent().parent(),
        content_section = container.find('.content');

    frm.submit(function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: {'search': frm.find("input[name='search']").val()},
            success: function (response) {

                content_section.html(response);

                var items = $('#content-list').children(":visible").length;
                var holder = content_section.find('.holder');

                if (items > 10) {
                    holder.jPages({
                        containerID : "content-list",
                        perPage: 10,
                        previous: "«",
                        next: "»",
                        midRange: 5
                    });
                }

                var li = $(".breadcrumb").find('li:last-child'),
                    li_text = $(li).html(),
                    new_li_text = container.data('breadtext');

                if (li_text == new_li_text) {
                    $(".breadcrumb").find('li:last-child').remove();
                }

                var new_li = $(li).clone();
                            
                new_li.html(new_li_text);

                $(li).html("<a href='" + container.data('breadurl') + "'>" + li_text + "</a>");
                $(li).append("<span class='divider'>/</span>");

                new_li.appendTo('.breadcrumb');
            },
            error: function(data) {
                setSearchSubmit();
            },
        });

        return false;
    });
}

$('.chat-collapse').on('shown.bs.collapse', function(e) {
    if($(this).is(e.target)){
        var li = $(".breadcrumb").find('li:last-child');
        var li_text = $(li).html();
        var url = $(".item_url").val();
        var new_li = $(li).clone();
        
        new_li.html($(this).parent().find('.panel-title .item_name').text());

        $(li).html("<a href='" + url + "'>" + li_text + "</a>");
        $(li).append("<span class='divider'>/</span>");

        new_li.appendTo('.breadcrumb');

        var content_section = $(this).find('.content');

        var url = $(this).data('url');

        setSearchSubmit();

        $.ajax({
            url: url,
            success: function (response) {
                content_section.html(response);

                var items = $('#content-list').children(":visible").length;
                var holder = content_section.find('.holder');

                if (items > 10) {
                    holder.jPages({
                        containerID : "content-list",
                        perPage: 10,
                        previous: "«",
                        next: "»",
                        midRange: 5
                    });
                }
            }
        });
    }
});

$('.chat-collapse').on('hidden.bs.collapse', function(e) {
    if($(this).is(e.target)){
        var last_txt = $(".breadcrumb").find('li:last-child').text(),
            participants_bread = $(this).data('breadtext');

        if (last_txt == participants_bread) {
            $(".breadcrumb").find('li:last-child').remove();            
        }

        $(".breadcrumb").find('li:last-child').remove();

        var li = $(".breadcrumb").find('li:last-child');
        var text = $(li).find('a').text();

        $(li).html(text);
    }
});