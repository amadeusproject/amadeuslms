var topic = {
  get: function (url, id_div, faz){
    if(!$(id_div + ' div').length || faz == 'true'){
      $.get(url, function(data){
        $(id_div).empty();
        $(id_div).append(data);
      });
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
