//controles do modal
$(window).ready(function() { // utilizado para abrir o modal quando tiver tido algum erro no preenchimento do formulario
  if($('.not_submited').length){
      $('#exam').modal('show');
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
    $('#exam').modal('hide');
      $.post(url,dados, function(data){
      }).fail(function(data){
        $("div.modal-backdrop.fade.in").remove();
        $("#modal_exam").empty();
        $("#modal_exam").append(data.responseText);
      });
  },
  remove: function(url,dados, id_li_link){
    $('#exam').modal('hide');
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        $("#modal_exam").empty();
        $("div.modal-backdrop.fade.in").remove();
      }).fail(function(){
        $("#modal_exam").empty();
        $("#modal_exam").append(data);
        $('#exam').modal('show');
      });
  }
}

alert("essfd");
