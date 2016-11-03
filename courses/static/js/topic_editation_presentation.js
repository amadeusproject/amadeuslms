$(document).ready(function(){
    $(".editation").css('display','none');
});
function show_editation(id_topic){
    $(".presentation_"+ id_topic).css('display','none');
    $(".editation_"+ id_topic).css('display','block');
};

function show_presentation(id_topic){
    $(".editation_"+ id_topic).css('display','none');
    $(".presentation_"+ id_topic).css('display','block');
};


