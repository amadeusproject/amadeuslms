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

var RemoveCourse = {
  remove: function(url,dados,id_li_link){
    $('#category').modal().hide();
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        // alert("certo");
        $('body').removeClass('modal-open');
        $("#modal_course").empty();
        $(".modal-backdrop.in").remove();
        alertify.success("Course removed successfully!");
        // setTimeout(function () { location.reload(1); }, 1);
      }).fail(function(){
        $("#modal_course").empty();
        $("#modal_course").append(data);
        $('#course').modal('show');
      });
  }
}

var delete_course = {
  get: function (url, id_modal, id_div_modal){
    $.get(url, function(data){
      if($(id_modal).length){
        $(id_div_modal).empty();
        $(id_div_modal).append(data);
      } else {
        $(id_div_modal).append(data);
      }
      $(id_modal).modal('show');
    });
  }
};

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

/*
*
* Functions to control category marker
*
*/
$('.collapse').on('show.bs.collapse', function (e) {
    if($(this).is(e.target)){
        var btn = $(this).parent().find('.fa-angle-right');
        
        btn.switchClass("fa-angle-right", "fa-angle-down", 250, "easeInOutQuad");

        var url = $(this).parent().find('.log_url').val();
        var log_input = $(this).parent().find('.log_id');

        $.ajax({
            url: url,
            data: {'action': 'open'},
            dataType: 'json',
            success: function (data) {
                log_input.val(data.log_id);
            },
            error: function (data) {
                console.log(data);
            }
        });
    }
});

$('.collapse').on('hide.bs.collapse', function (e) {
    if($(this).is(e.target)){
        var btn = $(this).parent().find('.fa-angle-down');
        
        btn.switchClass("fa-angle-down", "fa-angle-right", 250, "easeInOutQuad");

        var url = $(this).parent().find('.log_url').val();
        var log_id = $(this).parent().find('.log_id').val();

        $.ajax({
            url: url,
            data: {'action': 'close', 'log_id': log_id},
            dataType: 'json',
            success: function (data) {
                console.log(data.message);
            },
            error: function (data) {
                console.log(data);
            }
        });
    }
});