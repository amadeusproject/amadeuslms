$(function () {

  /* Script para abrir o modal com a imagem selecionada */
  $("#id_image").change(function () {
    if (this.files && this.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $("#image").attr("src", e.target.result);
        $("#modalCrop").modal("show");
      }
      reader.readAsDataURL(this.files[0]);
    }
  });

  /* Scripts da caixa de corte da imagem */
  var $image = $("#image");
  var cropBoxData;
  var canvasData;
  $("#modalCrop").on("shown.bs.modal", function () {
    $image.cropper({
      viewMode: 1 ,
      aspectRatio: 7/2,
      minCropBoxWidth: 200,
      minCropBoxHeight: 200,
      dragMode: 'move',
      ready: function () {
        $image.cropper("setCanvasData", canvasData);
        $image.cropper("setCropBoxData", cropBoxData);
      }
    });
  }).on("hidden.bs.modal", function () {
    cropBoxData = $image.cropper("getCropBoxData");
    canvasData = $image.cropper("getCanvasData");
    $image.cropper("destroy");
  });

  $(".js-zoom-in").click(function () {
    $image.cropper("zoom", 0.1);
  });

  $(".js-zoom-out").click(function () {
    $image.cropper("zoom", -0.1);
  });

  /* Script para pegar os valores das dimensões e depois fechar o modal */
  $(".js-crop-and-upload").click(function () {
    var cropData = $image.cropper("getData");
    $("#id_x").val(cropData["x"]);
    $("#id_y").val(cropData["y"]);
    $("#id_height").val(cropData["height"]);
    $("#id_width").val(cropData["width"]);
    $("#modalCrop").modal('hide');
  });

  /* Script para remover o arquivo enviado caso o usuário clique em cancelar*/
  $("#id_image").on('change', function(){
     console.log(this.value);
  });

  $('#crop_cancel').on('click', function(e){
      var input = $("#id_image");
      var holder = $("#pic_holder");
     input.replaceWith(input.val('').clone(true));
     holder.replaceWith(holder.val('').clone(true));
  });

});
