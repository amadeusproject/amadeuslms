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

            $('.date-picker').datepicker({
                format: 'dd/mm/yyyy',
            });

            var frm = $('#forum_create');
            frm.submit(function () {
                $.ajax({
                    type: frm.attr('method'),
                    url: frm.attr('action'),
                    data: frm.serialize(),
                    success: function (data) {
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
function editForum(url, forum, success_message) {
    $.ajax({
        url: url, 
        data: {'pk': forum},
        success: function(data) {
            $(".forum_form").html(data);

            $('.date-picker').datepicker({
                format: 'dd/mm/yyyy',
            });

            var frm = $('#forum_create');
            frm.submit(function () {
                $.ajax({
                    type: frm.attr('method'),
                    url: frm.attr('action'),
                    data: frm.serialize(),
                    success: function (data) {
                        $('.forum_view').html(data);

                        alertify.success(success_message);

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
function edit_post(url, post_id, success_message) {
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
                        alertify.success(success_message);

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

/*
*
* Function to load more posts
*
*/
function load_more_posts(pageNum, numberPages, url) {
    // Remove button from the template
    $("#load_more_posts").remove();
    
    // Check if page is equal to the number of pages
    if (pageNum == numberPages) {
        return false
    }

    pageNum += 1;

    // Show loader
    $("#loading_posts").show();

    // Configure the url we're about to hit
    setTimeout(function (){
        $.ajax({
            url: url, 
            data: {'page': pageNum},
            success: function(data) {
                $("#loading_posts").hide();
                
                $("#posts_list").append(data);
            },
            error: function(data) {
                console.log(data);
                console.log('Error');
            }
        });
    }, 1000)
};

/*
*
* Function to load answer post form and set the submit function
*
*/
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

/*
*
* Function to load form to edit post answer
*
*/
function edit_post_answer(url, answer_id, success_message) {
    $.ajax({
        url: url,
        success: function(data) {
            $("#answer_"+answer_id).find(".post_answer_content").hide();
            $("#answer_"+answer_id).find(".post_answer_content").after(data);

            var frm = $("#answer_"+answer_id).find(".answer_post_form");
            frm.submit(function () {
                $.ajax({
                    type: frm.attr('method'),
                    url: frm.attr('action'),
                    data: frm.serialize(),
                    success: function (data) {
                        alertify.success(success_message);

                        $("#answer_"+answer_id).parent().after(data);
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
* Function to cancel post answer edition
*
*/
function cancelEditPostAnswer(answer_id) {
    $("#answer_"+answer_id).find(".post_answer_content").show();
    $("#answer_"+answer_id).find(".answer_post_form").remove();    
}

/*
*
* Function to delete an answer
*
*/
function delete_answer(url, answer, message) {
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
                    $("#answer_"+answer).remove();
                });
            }
        });
    });
}

/*
*
* Function to load more answers of a post
*
*/
function load_more_answers(post_id, pageNum, numberPages, url) {
    // Remove button from the template
    $("#post_"+post_id).find(".load_more_answers").remove();
    
    // Check if page is equal to the number of pages
    if (pageNum == numberPages) {
        return false
    }

    pageNum += 1;

    // Show loader
    $("#post_"+post_id).find(".loading_answers").show();

    // Configure the url we're about to hit
    setTimeout(function (){
        $.ajax({
            url: url, 
            data: {'page_answer': pageNum},
            success: function(data) {
                $("#post_"+post_id).find(".loading_answers").hide();
                
                $("#post_"+post_id).find(".answer_list").append(data);
            }
        });
    }, 1000)
};