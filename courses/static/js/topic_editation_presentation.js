
$(document).ready(function(){
    $(".editation").hide();  
});

function show_editation(id_topic){
    $(".presentation_"+ id_topic).hide();
    $(".editation_"+ id_topic).show();
    $('#summernote').summernote({height: 300});
};

function show_presentation(id_topic){
    $(".editation_"+ id_topic).hide();
    $(".presentation_"+ id_topic).show();
};
