/*
*
* Function to load forum to modal
*
*/
function showForum(url, forum_id) {
    $.ajax({
        url: url, 
        data: {'forum_id': forum_id},
        success: function(data) {
            $(".forum_topics").html(data);
        }
    });

    $('#forumModal').modal();
}

function getForm(url) {
    $.ajax({
        url: url, 
        success: function(data) {
            $(".forum_form").html(data);
        }
    });

    $(".forum_form").show();
}

function showPosts(url, forum) {
    if ($("#collapse" + forum).hasClass('in')) {
        $("#collapse" + forum).collapse('hide');
    } else {
        $.ajax({
            url: url, 
            data: {'forum': forum},
            success: function(data) {
                $("#collapse" + forum).find(".well").html(data);
            }
        });

        $("#collapse" + forum).collapse('show');
    }
}

function showPostsAnswers(url, post) {
    if ($("#collapse" + post).hasClass('in')) {
        $("#collapse" + post).collapse('hide');
    } else {
        $.ajax({
            url: url, 
            data: {'post': post},
            success: function(data) {
                $("#collapse" + post).find(".well").html(data);
            }
        });

        $("#collapse" + post).collapse('show');
    }
}