
var Submite = {
  remove: function(url,dados,id_li_link){
    $('#category').modal('hide');
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        $("#modal_category").empty();
        $("div.modal-backdrop.fade.in").remove();
        alertify.success("Category removed successfully!");
      }).fail(function(){
        $("#modal_category").empty();
        $("#modal_category").append(data);
        $('#category').modal('show');
      });
  }
}

var modal = {
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