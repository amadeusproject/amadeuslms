var topic = {
  get: function (button, url, id_div, faz){
    if(!$(id_div + ' div').length || faz == 'true'){
        var opened = $("#topics").find(".fa-angle-up");
        
        if (opened.length > 0) {
            opened.removeClass("fa-angle-up");
            opened.addClass("fa-angle-down");
            var op_topic = opened.parent().parent().parent().parent().parent();

            var log_id = op_topic.find(".log_id").val();
            var log_url = op_topic.find(".log_url").val();

            topicLog(log_url, log_id, 'close', id_div);

            op_topic.find(".loaded").val("false");
        }

        //Changing button icon
        button.find("i").removeClass('fa-angle-down');
        button.find("i").addClass('fa-angle-up');
        
        $.get(url, function(data){
            $(id_div).empty();
            $(id_div).append(data);
        });
    } else {
        var loaded = $(id_div).find(".loaded").val();

        if (loaded == "true") {
            var opened = $("#topics").find(".fa-angle-up");
        
            opened.removeClass("fa-angle-up");
            opened.addClass("fa-angle-down");
            var op_topic = opened.parent().parent().parent().parent().parent();

            var log_id = op_topic.find(".log_id").val();
            var log_url = op_topic.find(".log_url").val();

            topicLog(log_url, log_id, 'close', id_div);

            $(id_div).find(".loaded").val("false");
        } else {
            var opened = $("#topics").find(".fa-angle-up");
        
            opened.removeClass("fa-angle-up");
            opened.addClass("fa-angle-down");
            var op_topic = opened.parent().parent().parent().parent().parent();

            var log_id = op_topic.find(".log_id").val();
            var log_url = op_topic.find(".log_url").val();

            topicLog(log_url, log_id, 'close', op_topic);

            op_topic.find(".loaded").val("false");

            var opened = $(id_div).parent().parent().find(".fa-angle-down");
            opened.removeClass("fa-angle-down");
            opened.addClass("fa-angle-up");
            
            var log_url = $(id_div).find(".log_url").val();

            topicLog(log_url, 0, 'open', id_div);
        }
    }
  },
  post: function(url,dados,id_div){
      $.post(url,dados, function(data){
        $(id_div).empty();
        $.ajax({
          method: "get",
          url: data['url'],
          success: function(view){
            $(id_div).append(view);
          }
        });
        alertify.success("Topic updated successfully!");
      }).fail(function(data){
        $(id_div).empty();
        $(id_div).append(data);
      });
  }
};
var delete_topic = {
  get: function (url, id_modal, id_div_modal){
    $.get(url, function(data){
      if($(id_modal).length){
        $(id_div_modal).empty();
      }
      $(id_div_modal).append(data);
      $(id_modal).modal('show');
    });
  }
};

function topicLog(url, topic_log_id, action, topic_div) {
    $.ajax({
        url: url,
        data: {'action': action, 'log_id': topic_log_id},
        dataType: 'json',
        success: function (data) {
            if (action == 'open') {
                $(topic_div).find(".log_id").val(data.log_id);
                $(topic_div).find(".loaded").val("true");
            }
        },
        error: function(data) {
            console.log('Error: ');
            console.log(data);
        }
    })
}