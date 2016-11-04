var RemoveSubject = {
  remove: function(url,dados,id_li_link){
    $('#subject').modal('hide');
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        $("#modal_subject").empty();
        $("#accordion").remove();
        $(".modal-backdrop.in").remove();
        alertify.success("Subject removed successfully!");
        setTimeout(function () { location.reload(1); }, 2000);
      }).fail(function(){
        $("#modal_subject").empty();
        $("#modal_subject").append(data);
        $('#subject').modal('show');
      });
  }
}

var delete_subject = {
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