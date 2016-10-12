function get(url, id_modal, id_div_modal){
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

// function remove(url, id_li_link){
//   $.post(url, function(data){
//     $(id_li_link).remove();
//   }).fail(function(data){
//     alert("Error ao excluir a enquete");
//     alert(data);
//   });
// }
