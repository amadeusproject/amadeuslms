function get_modal_file(url, id, div_content){
    
    $.get(url, function (data) {
        $(div_content).empty();
        $(div_content).append(data);
        $(id).modal('show');
    });

}

// $(document).ready(function (){
//     // alert('Oi');
//     var frm = $("#form-file");
//     frm.submit(function(event) {
//         $.ajax({
//             type: frm.attr('method'),
//             url: frm.attr('action'),
//             data: {
//                 'file_url': $('#id_file_url'),
//                 'name': $('#id_name'),
//                 csrfmiddlewaretoken: csrf
//             },
//             success: function (data) {
//                 alert(data);
//                 // $("#posts_list").append(data);
//                 // frm[0].reset();
//             },
//             processData : false,
//             error: function(data) {
//                 alert('Error');
//                 // console.log(frm.serialize());
//                 // console.log('Error');
//             }
//         });
//         $('#fileModal').modal('hide');
//         event.preventDefault();
//     });
// });

// var Submite = {
//   post: function(url,dados){
//     $('#fileModal').modal('hide');
//       $.post(url,dados, function(data){
//       }).fail(function(data){
//         $("div.modal-backdrop.fade.in").remove();
//         $("#modal_poll").empty();
//         $("#modal_poll").append(data.responseText);
//       });
//   }
//   ,
//   remove: function(url,dados, id_li_link){
//     $('#fileModal').modal('hide');
//       $.post(url,dados, function(data){
//         $(id_li_link).remove();
//         $("#modal_poll").empty();
//         $("div.modal-backdrop.fade.in").remove();
//       }).fail(function(){
//         $("#modal_poll").empty();
//         $("#modal_poll").append(data);
//         $('#fileModal').modal('show');
//       });
//   }
// }