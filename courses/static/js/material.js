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


function createMaterial(url, topic) {
    $.ajax({
        url: url, 
        data: {'topic': topic},
        success: function(data) {
            $(".material_form").html(data);
            $("#id_topic").val(topic);

            setMaterialCreateFormSubmit();
        }
    });

    $("#editFileModal").modal();
}

function setMaterialCreateFormSubmit() {
    
    var frm = $('#material_create');
    frm.submit(function () {
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function (data) {
                data = data.split('-');

                $('.foruns_list').append("<li><i class='fa fa-commenting' aria-hidden='true'></i> <a id='forum_"+data[1]+"' href='"+data[0]+"'> "+data[2]+"</a></li>");

                $("#createForum").modal('hide');

                showForum(data[0], data[1]);
            },
            error: function(data) {
                $(".forum_form").html(data.responseText);
                setMaterialCreateFormSubmit();
            }
        });
        return false;
    });
}

function setMaterialUpdateFormSubmit(success_message) {

    var frm = $('#material_create');
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

                setMaterialUpdateFormSubmit(success_message);
            }
        });
        return false;
    });
}