//deve ser importado apenas depois do html
$( "#form" ).sortable({ // utilizado para fazer a re-organização das respostas
    delay: 100,
    distance: 5,
    update: function( event, ui ) {
      var cont = 1;
      $("#form div div div input").each(function(){
              $(this).attr('name',cont++);
      });
    },
});
