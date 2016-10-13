//controles do modal
$(window).ready(function() { // utilizado para abrir o modal quando tiver tido algum erro no preenchimento do formulario
  if($('.not_submited').length){
      $('#poll').modal('show');
  }
});
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
  post: function(url,dados){
    $('#poll').modal('hide');
      $.post(url,dados, function(data){
      }).fail(function(data){
        $("div.modal-backdrop.fade.in").remove();
        $("#modal_poll").empty();
        $("#modal_poll").append(data.responseText);
      });
  }
  ,
  remove: function(url,dados, id_li_link){
    $('#poll').modal('hide');
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        $("#modal_poll").empty();
        $("div.modal-backdrop.fade.in").remove();
      }).fail(function(){
        $("#modal_poll").empty();
        $("#modal_poll").append(data);
        $('#poll').modal('show');
      });
  }
}
