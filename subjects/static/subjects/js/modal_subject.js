var RemoveSubject = {
  remove: function(url,dados,id_li_link){
    $("#subject").modal('toggle');
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        $('body').removeClass('modal-open');
        $("#modal_course").empty();
        $(".modal-backdrop.in").remove();
        alertify.success("Subject removed successfully!");
      }).fail(function(){
        $("#modal_course").empty();
        $("#modal_course").append(data);
        $('#subject').modal('show');
      });
  }
}
var delete_subject = {
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