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
