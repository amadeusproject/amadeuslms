$(".edit_card").on('click', function() {
    $(".presentation").css('display','none');
    $(".editation").css('display','block');
})
$(".edit_card_end").on('click', function() {
    $(".editation").css('display','none');
    $(".presentation").css('display','block');
})