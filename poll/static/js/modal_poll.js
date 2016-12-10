
var Answer = {
    init: function(url) { // utilizado para adicionar um novo campo de resposta
      $.get(url, function(data){
        $("#form").append(data);
        var cont = 1;
        $("#form div div div input").each(function(){
                $(this).attr('name',cont++);
        });
      });
    }
};

var Submite = {
  create: function(url,dados, slug){
    $('#poll').modal('hide');
    var poll = null;
      $.post(url,dados, function(data){
        $.ajax({
          method: "get",
          url: data["view"],
          success: function(view){
            $('#list-topic-'+ slug +'-poll').append(view);
          }
        });
        $.ajax({
          method: "get",
          url: data["edit"],
          success: function(edit){
            $('#list-topic-'+ slug +'-poll-edit').append(edit);
          }
        });
        $("#requisicoes_ajax").empty();
        $('body').removeClass('modal-open');
        alertify.success('Poll successfully created!');
        $("div.modal-backdrop.fade.in").remove();
      }).fail(function(data){
        $("div.modal-backdrop.fade.in").remove();
        $("#requisicoes_ajax").empty();
        $("#requisicoes_ajax").append(data.responseText);
        $('#poll').modal('show');
      });
  },
  update: function(url,dados, slug_poll, slug_topic){
    $('#poll').modal('hide');
      $.post(url,dados, function(data){
        $('#list-topic-'+ slug_topic +'-poll #'+slug_poll).replaceWith(data);
        $('#list-topic-'+ slug_topic +'-poll #'+slug_poll).replaceWith(data);
        $('body').removeClass('modal-open');
        alertify.success('Poll successfully updated!')
      }).fail(function(data){
        $("div.modal-backdrop.fade.in").remove();
        $("#requisicoes_ajax").empty();
        $("#requisicoes_ajax").append(data.responseText);
        $('#poll').modal('show');
      });
  },
  remove: function(url,dados, id_li_link){
    $('#poll').modal('hide');
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        $(id_li_link+"_div").remove();
        $('body').removeClass('modal-open');
        $("#requisicoes_ajax").empty();
        $("div.modal-backdrop.fade.in").remove();
        alertify.success('Poll successfully removed')
      }).fail(function(){
        $("#requisicoes_ajax").empty();
        $("#requisicoes_ajax").append(data);
        $('#poll').modal('show');
      });
  },
  answer: function(url,dados){
    $('#poll').modal('hide');
      $.post(url,dados, function(data){
        alertify.success('Poll successfully answered!')
      }).fail(function(data){
        $("div.modal-backdrop.fade.in").remove();
        $("#requisicoes_ajax").empty();
        $("#requisicoes_ajax").append(data.responseText);
        $('#poll').modal('show');
      });
  }
}
