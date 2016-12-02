var Submite = {
  remove: function(url,dados,id_li_link){
    $('#category').modal('hide');
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        $("#modal_remove_cat").empty();
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

// var modal = {
//   get: function (url, id_modal, id_div_modal){
//     $.get(url, function(data){
//       if($(id_modal).length){
//         $(id_div_modal).empty();
//         $(id_div_modal).append(data);
//       } else {
//         $(id_div_modal).append(data);
//       }
//       $(id_modal).modal('show');
//     });
//   }
// };
