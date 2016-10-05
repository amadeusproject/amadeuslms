/*
*
* Function to get a cookie stored on browser
*
*/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/*
*
* Defining action of the form to make a post in forum
*
*/
$(document).ready(function (){
    var frm = $('#form_post');
    frm.submit(function () {
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function (data) {
                $("#posts_list").append(data);
                frm[0].reset();
            },
            error: function(data) {
                console.log(frm.serialize());
                console.log('Error');
            }
        });
        return false;
    });
});

/*
*
* Function to load create forum's form and set the submit function
*
*/
function createForum(url, topic) {
    $.ajax({
        url: url, 
        data: {'topic': topic},
        success: function(data) {
            $(".forum_form").html(data);
            $("#id_topic").val(topic);

            $('.date-picker').datepicker();

            var frm = $('#forum_create');
            frm.submit(function () {
                $.ajax({
                    type: frm.attr('method'),
                    url: frm.attr('action'),
                    data: frm.serialize(),
                    success: function (data) {
                        console.log(data);
                        data = data.split('-');

                        $('.foruns_list').append("<a id='forum_"+data[1]+"' href='"+data[0]+"'>"+data[2]+"<br /></a>");

                        $("#createForum").modal('hide');

                        showForum(data[0], data[1]);
                    },
                    error: function(data) {
                        $(".forum_form").html(data.responseText);
                    }
                });
                return false;
            });
        }
    });

    $("#createForum").modal();
}

/*
*
* Function to load edit forum's form and set the submit function
*
*/
function editForum(url, forum) {
    $.ajax({
        url: url, 
        data: {'pk': forum},
        success: function(data) {
            $(".forum_form").html(data);
            //$("#id_topic").val(topic);

            $('.date-picker').datepicker();

            var frm = $('#forum_create');
            frm.submit(function () {
                $.ajax({
                    type: frm.attr('method'),
                    url: frm.attr('action'),
                    data: frm.serialize(),
                    success: function (data) {
                        $('.forum_view').html(data);

                        $("#editForum").modal('hide');
                    },
                    error: function(data) {
                        $(".forum_form").html(data.responseText);
                    }
                });
                return false;
            });
        }
    });

    $("#editForum").modal();
}

/*
*
* Function to delete a forum
*
*/
function delete_forum(url, forum, message, return_url) {
    alertify.confirm(message, function(){
        var csrftoken = getCookie('csrftoken');
        
        $.ajax({
            method: 'post',
            beforeSend: function (request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            },
            url: url, 
            success: function(data) {
                alertify.alert('Amadeus', data, function(){
                    window.location.href = return_url;
                });
            }
        });
    });
}

/*
*
* Function to load form to edit post
*
*/
function edit_post(url, post_id) {
    $.ajax({
        url: url,
        success: function(data) {
            $("#post_"+post_id).find(".post_content").hide();
            $("#post_"+post_id).find(".post_content").after(data);

            var frm = $("#post_"+post_id).find(".edit_post_form");
            frm.submit(function () {
                $.ajax({
                    type: frm.attr('method'),
                    url: frm.attr('action'),
                    data: frm.serialize(),
                    success: function (data) {
                        $("#post_"+post_id).parent().after(data);
                        frm.parent().parent().remove();
                    },
                    error: function(data) {
                        console.log(frm.serialize());
                        console.log('Error');
                    }
                });
                return false;
            });
        }
    });
}

/*
*
* Function to cancel post edition
*
*/
function cancelEditPost(post_id) {
    $("#post_"+post_id).find(".post_content").show();
    $("#post_"+post_id).find(".edit_post_form").remove();    
}

/*
*
* Function to delete a post
*
*/
function delete_post(url, post) {
    var csrftoken = getCookie('csrftoken');
    
    $.ajax({
        method: 'post',
        beforeSend: function (request) {
            request.setRequestHeader('X-CSRFToken', csrftoken);
        },
        url: url, 
        success: function(data) {
            $("#post_"+post).remove();
        }
    });
}

function answer(id, url) {
    $.ajax({
        url: url, 
        success: function(data) {
            $("#post_"+id).find(".answer_post").html(data);
            $("#post_"+id).find("#id_post").val(id);

            var frm = $("#post_"+id).find(".answer_post_form");
            frm.submit(function () {
                $.ajax({
                    type: frm.attr('method'),
                    url: frm.attr('action'),
                    data: frm.serialize(),
                    success: function (data) {
                        $("#post_"+id).find(".answer_list").append(data);

                        $("#post_"+id).find(".answer_post").hide();
                    },
                    error: function(data) {
                        console.log(frm.serialize());
                        console.log('Error');
                    }
                });
                return false;
            });
        }
    });

    $("#post_"+id).find(".answer_post").show();
}