var Modal = {
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
alert("req");
