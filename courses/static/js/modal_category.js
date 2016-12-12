var Submite = {
  remove: function(url,dados,id_li_link){
    $('#category').modal('hide');
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        $("#modal_remove_cat").empty();
        $('body').removeClass('modal-open');
        $(id_li_link).remove();
        $(".modal-backdrop.in").remove();
        alertify.success("Category removed successfully!");
      }).fail(function(){
        $("#modal_remove_cat").empty();
        $("#modal_remove_cat").append(data);
        $('#category').modal('show');
      });
  }
}
