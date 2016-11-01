var locale = navigator.language || navigator.userLanguage;

$('.date-picker').datepicker({
    language: locale,
});

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
* Function to subscribe (works for courses and subjects)
*
*/
function subscribe(elem, url, id, confirm_message) {
	alertify.confirm(confirm_message, function(){
		$.ajax({
			dataType: "json",
			url: url,
			success: function (data) {
				if (data.status == "ok") {
					elem.remove();
					alertify.success(data.message);
					$(".panel_"+id).find(".view_btn").show()
				} else {
					alertify.error(data.message);
				}
			}
		});
	});
}

/*
*
* Function to delete a course
*
*/
function delete_course(url, course, message, return_url) {
    alertify.confirm(message, function(){
        var csrftoken = getCookie('csrftoken');

        $.ajax({
            method: 'post',
            beforeSend: function (request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            },
            url: url,
            success: function(data) {
                alertify.alert('Remove Course', 'Course removed successfully!', function(){
                    window.location.href = return_url;
                });
            }
        });
    });
}
/* 
*
* Function to load create course's form
*
*/
function replicate_course(url, course) {
    $.ajax({
        url: url,
        data: {'form': course},
        success: function(data) {
            $(".course_replicate_form").html(data);
        }
    });
}