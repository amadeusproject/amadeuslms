var new_posts = []; //Store the new posts ids
var new_answers = {};
var locale = navigator.language || navigator.userLanguage;
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
            dataType: 'json',
            success: function (data) {
                if ($("#load_more_posts").length == 0) {
                    $("#posts_list").append(data.html);
                } else {
                    $("#load_more_posts").before(data.html);
                }

                new_posts.push(data.new_id);

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
* Function to load create forum's form
*
*/
function createForum(url, topic) {
    $.ajax({
        url: url, 
        data: {'topic': topic},
        success: function(data) {
            $(".forum_form").html(data);
            $("#id_topic").val(topic);

            setForumCreateFormSubmit(topic);
        }
    });

    $("#createForum").modal();
}

/*
*
* Function to set the forum's create form submit function
*
*/
function setForumCreateFormSubmit(topic) {
    $('.date-picker').datepicker({
        language: locale,
        startDate: "dateToday"
    });

    var frm = $('#forum_create');
    frm.submit(function () {
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            dataType: "json",
            success: function (data) {
                $(".topic_" + topic).find('.foruns_list').append("<li><i class='fa fa-commenting' aria-hidden='true'></i> <a id='forum_"+data.forum_id+"' href='"+data.url+"'> "+data.name+"</a></li>");

                alertify.success(data.message);

                $("#createForum").modal('hide');
            },
            error: function(data) {
                $(".forum_form").html(data.responseText);
                setForumCreateFormSubmit(topic);
            }
        });
        return false;
    });
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

            setForumUpdateFormSubmit(success_message);
        }
    });

    $("#editForum").modal();
}

/*
*
* Function to set the forum's update form submit function
*
*/
function setForumUpdateFormSubmit(success_message) {
    $('.date-picker').datepicker({
        language: locale,
        startDate: "dateToday"
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

                setForumUpdateFormSubmit(success_message);
            }
        });
        return false;
    });
}

/*
*
* Function to delete a forum
*
*/
function delete_forum(url, forum, message, return_url) {
    alertify.confirm(message, function(){
        var csrftoken = Cookies.get('csrftoken');
        
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

                        $("#post_"+post_id).parent().after(data.html);
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
    var csrftoken = Cookies.get('csrftoken');
    
    $.ajax({
        method: 'post',
        beforeSend: function (request) {
            request.setRequestHeader('X-CSRFToken', csrftoken);
        },
        url: url, 
        success: function(data) {
            alertify.success(data);

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

    var showing = new_posts.join(',');

    // Show loader
    $("#loading_posts").show();

    // Configure the url we're about to hit
    setTimeout(function (){
        $.ajax({
            url: url, 
            data: {'page': pageNum, 'showing': showing},
            dataType: 'json',
            success: function(data) {
                $("#loading_posts").hide();

                var child = $("#posts_list").find(".new_post:first");

                if (child.length == 0) {
                    $("#posts_list").append(data.html);
                } else {
                    child.before(data.html);
                }

                if (data.page != data.num_pages) {
                    $("#posts_list").append('<a id="load_more_posts" href="javascript:load_more_posts(' + data.page + ',' + data.num_pages + ',\'' + url + '\');" class="btn btn-raised btn-primary btn-block">' + data.btn_text + '</a>');
                }
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
                    dataType: 'json',
                    success: function (data) {
                        $("#post_"+id).find(".answer_post").hide();

                        if ($("#post_"+id).find(".load_more_answers").length == 0) {
                            $("#post_"+id).find(".answer_list").append(data.html);
                        } else {
                            $("#post_"+id).find(".load_more_answers").before(data.html);
                        }

                        if (typeof(new_answers[id]) == 'undefined') {
                            new_answers[id] = [];
                        }

                        new_answers[id].push(data.new_id);
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

                        $("#answer_"+answer_id).parent().after(data.html);
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
        var csrftoken = Cookies.get('csrftoken');
        
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

    var showing;

    if (typeof(new_answers[post_id]) == 'undefined') {
        showing = "";
    } else {
        showing = new_answers[post_id].join(',');
    }

    // Show loader
    $("#post_"+post_id).find(".loading_answers").show();

    // Configure the url we're about to hit
    setTimeout(function (){
        $.ajax({
            url: url, 
            data: {'page_answer': pageNum, 'showing_ans': showing},
            dataType: 'json',
            success: function(data) {
                $("#post_"+post_id).find(".loading_answers").hide();
                
                var child = $("#post_"+post_id).find(".answer_list").find(".new_answer:first");

                if (child.length == 0) {
                    $("#post_"+post_id).find(".answer_list").append(data.html);
                } else {
                    child.before(data.html);
                }

                if (data.page != data.num_pages) {
                    $("#post_"+post_id).find(".answer_list").append('<a href="javascript:load_more_answers(' + post_id + ',' + data.page + ',' + data.num_pages + ',\'' + url + '\');" class="btn btn-raised btn-primary btn-block load_more_answers">' + data.btn_text + '</a>');
                }
            }
        });
    }, 1000)
};