/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

var new_posts = [];
var new_comments = {};

$(function () {
    $(".post-field").click(function () {
        var url = $(this).find('h4').data('url');

        $.ajax({
            url: url,
            success: function (data) {
                $('#post-modal-form').html(data);

                setPostFormSubmit();

                $('#post-modal-form').modal('show');
            }
        });
    });

    $(".comment-section:visible").each(function () {
        var height = $(this)[0].scrollHeight;

        $(this).animate({scrollTop: height}, 0);
    });
    
    postHeightLimits();
    setUserDataPopover();

});

function setUserDataPopover() {
    $('[data-toggle="popover"]').popover({
        html: true,
        placement: function () {
            return window.innerWidth <= 768 ? 'bottom' : 'right';
        },
        content: function () {
            return $(this).parent().find(".popover").html();
        }
    }).on('show.bs.popover', function (e) {
        $('[data-toggle="popover"]').not(e.target).popover('hide');
    }).on('shown.bs.popover', function (e) {
        if($(this).is(e.target)){
            var popover = $(".popover.fade.in"),
                buttons = popover.parent().find('a'),
                close = popover.parent().find('.close:visible');

            popover.animate({
                'max-width': '330px',
            }, 0);

            popover.find('.popover-content').animate({
                padding: '9px 5px',
            }, 0);

            popover.find('h4').animate({
                'font-size': '16px',
            }, 0);

            close.on("click", function () {
                popover.popover('hide');
            }); 

            buttons.on("click", function () {
                popover.popover('hide');
            })
        }
    });
}

function postHeightLimits() {
    $('.post-body').each(function () {
        if ($(this).outerHeight() > 500) {
            var post = $(this),
                btn = post.parent().find('.see-complete');

            post.attr('style', 'overflow:hidden;max-height:500px');

            btn.attr('style', 'display:block');

            btn.click(function () {
                seeComplete($(this), post);
            });
        }
    });
}

function seeComplete(btn, post) {
    post.attr('style', '');

    btn.attr('style', 'display:none');
}

function setPostFormSubmit(post = "") {
    var frm = $('#post-form');

    frm.submit(function (e) {
        var btn = frm.parent().parent().parent().find("button[form='post-form']");

        btn.prop('disable', true);
        btn.prop('disabled', true);

        var formData = new FormData($(this)[0]);

        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: formData,
            dataType: "json",
            async: false,
            success: function (data) {
                if (post != "") {
                    var old = $("#post-" + post);

                    old.before(data.view);

                    old.remove();
                } else {
                    $('.posts:visible').prepend(data.view);

                    new_posts.push(data.new_id);

                    $('.no-subjects:visible').attr('style', 'display:none');
                }

                setUserDataPopover();
                setTimeout(function () { postHeightLimits() }, 100);

                $('#post-modal-form').modal('hide');

                alertify.success(data.message);
            },
            error: function(data) {
                $("#post-modal-form").html(data.responseText);
                setPostFormSubmit(post);
            },
            cache: false,
            contentType: false,
            processData: false
        });

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

function editPost(btn) {
    var url = btn.data('url');
    var post = btn.data('post');

    $.ajax({
        url: url,
        success: function (data) {
            $('#post-modal-form').html(data);

            setPostFormSubmit(post);

            $('#post-modal-form').modal('show');
        }
    });
}

function deletePost(btn) {
    var url = btn.data('url');
    var post = btn.data('post');

    $.ajax({
        url: url,
        success: function (data) {
            $('#post-modal-form').html(data);

            setPostDeleteSubmit(post);

            $('#post-modal-form').modal('show');
        }
    });
}

function setPostDeleteSubmit (post) {
    var frm = $("#delete_form");

    frm.submit(function () {
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function (response) {
                $("#post-" + post).remove();

                $('#post-modal-form').modal('hide');

                alertify.success(response.msg);
            },
            error: function (data) {
                console.log(data);
            }
        });

        return false;
    });
}

function comment(field) {
    var url = field.find('h4').data('url'),
        post = field.find('h4').data('post');

    $.ajax({
        url: url,
        success: function (data) {
            $('#post-modal-form').html(data);

            setCommentFormSubmit(post);

            $('#post-modal-form').modal('show');
        }
    });
}

function editComment(btn) {
    var url = btn.data('url'),
        post = btn.data('post'),
        comment = btn.data('id');

    $.ajax({
        url: url,
        success: function (data) {
            $('#post-modal-form').html(data);

            setCommentFormSubmit(post, comment);

            $('#post-modal-form').modal('show');
        }
    });
}

function setCommentFormSubmit(post, comment = "") {
    var frm = $('#comment-form');

    frm.submit(function () {
        var btn = frm.parent().parent().parent().find("button[form='comment-form']")

        btn.prop('disable', true);
        btn.prop('disabled', true);

        var formData = new FormData($(this)[0]);

        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: formData,
            dataType: "json",
            async: false,
            success: function (data) {
                if (comment != "") {
                    var old = $("#comment-" + comment);

                    old.before(data.view);

                    old.remove();
                } else {
                    $("#post-" + post).find(".comment-section").append(data.view);

                    if (typeof(new_comments[post]) == 'undefined') {
                        new_comments[post] = [];
                    }

                    new_comments[post].push(data.new_id);
                }

                $('#post-modal-form').modal('hide');

                alertify.success(data.message);
            },
            error: function(data) {
                $("#post-modal-form").html(data.responseText);
                setCommentFormSubmit(post, comment);
            },
            cache: false,
            contentType: false,
            processData: false
        });

        return false;
    });
}

function deleteComment(btn) {
    var url = btn.data('url');
    var comment = btn.data('id');

    console.log(comment);

    $.ajax({
        url: url,
        success: function (data) {
            $('#post-modal-form').html(data);

            setCommentDeleteSubmit(comment);

            $('#post-modal-form').modal('show');
        }
    });
}

function setCommentDeleteSubmit (comment) {
    var frm = $("#delete_form");

    frm.submit(function () {
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function (response) {

                $("#comment-" + comment).remove();

                $('#post-modal-form').modal('hide');

                alertify.success(response.msg);
            },
            error: function (data) {
                console.log(data);
            }
        });

        return false;
    });
}

function loadComments (btn) {
    var url = btn.data('url'),
        post = btn.data('post'),
        page = btn.parent().data('page'),
        loading = btn.parent().find('.loading');

    page = parseInt(page);
    page = page + 1;

    loading.show();
    btn.hide();

    var showing;

    if (typeof(new_comments[post]) == 'undefined') {
        showing = "";
    } else {
        showing = new_comments[post].join(',');
    }

    $.ajax({
        url: url,
        data: {'page': page, 'showing': showing},
        dataType: 'json',
        success: function (response) {
            loading.hide();
            btn.show();

            btn.after(response.loaded);

            setUserDataPopover();
        }
    });
}
