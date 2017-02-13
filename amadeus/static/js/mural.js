var new_posts = [];
var new_comments = {};
// loadOnScroll handler
var loadOnScroll = function() {
   // If the current scroll position is past out cutoff point...
    if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
        // temporarily unhook the scroll event watcher so we don't call a bunch of times in a row
        $(window).unbind();
        // execute the load function below that will visit the view and return the content
        loadPosts();
    }
};

var loadPosts = function() {
    var loadUrl = $('.mural').data('url'),
        pageNum = $('.mural').data('page'),
        numberPages = $('.mural').data('pages'),
        favorites = $('.mural').data('fav'),
        mine = $('.mural').data('mine'),
        showing = new_posts.join(',');
    // Check if page is equal to the number of pages
    if (pageNum == numberPages) {
        return false
    }
    // Update the page number
    pageNum = pageNum + 1;

    $("#loading_posts").show();
    // Configure the url we're about to hit
    setTimeout(function (){
        $.ajax({
            url: loadUrl,
            data: {'page': pageNum, "favorite": favorites, "mine": mine, "showing": showing},
            success: function(data) {
                $("#loading_posts").hide();

                $(".posts").append(data);

                $('.mural').data('page', pageNum);

                setTimeout(function () { postHeightLimits() }, 10);
            },
            complete: function(data, textStatus){
                // Turn the scroll monitor back on
                $(window).bind('scroll', loadOnScroll);
            }
        });
    }, 1000)
};

$(function () {
    $(window).bind('scroll', loadOnScroll);
    
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

    $("#clear_filter").click(function () {
        var frm = $(this).parent();

        frm.find("input[type='checkbox']").prop('checked', false);

        frm.submit();
    });

    $(".comment-section").each(function () {
        var height = $(this)[0].scrollHeight;

        $(this).animate({scrollTop: height}, 0);
    });

    postHeightLimits();

});

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

    frm.submit(function () {
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
                    $('.posts').prepend(data.view);
    
                    new_posts.push(data.new_id);

                    $('.no-subjects').attr('style', 'display:none');
                }

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
                setPostFormSubmit(post, comment);
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
        }
    });
}