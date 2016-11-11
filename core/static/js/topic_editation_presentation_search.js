
var x = 0;
$(".edit_card").on('click', function() {
    $(".presentation").css('display','none');
    $(".editation").css('display','block');
})
$(".edit_card_end").on('click', function() {
    $(".editation").css('display','none');
    $(".presentation").css('display','block');
})

$("#bot").on('click', function(){
	x = x+1;
	console.log(2)
	if(x%2 == 0){
		console.log(0)
	$("#down").attr('class', 'fa fa-caret-square-o-down');
}
else{
	console.log(1)
	$("#down").attr('class', 'fa fa-caret-square-o-up');
}

})
$("#bot1").on('click', function(){
	x = x+1;
	console.log(2)
	if(x%2 == 0){
		console.log(0)
	$("#down1").attr('class', 'fa fa-caret-square-o-down');
}
else{
	console.log(1)
	$("#down1").attr('class', 'fa fa-caret-square-o-up');
}

})

$("#bot2").on('click', function(){
	x = x+1;
	console.log(2)
	if(x%2 == 0){
		console.log(0)
	$("#down2").attr('class', 'fa fa-caret-square-o-down');
}
else{
	console.log(1)
	$("#down2").attr('class', 'fa fa-caret-square-o-up');
}

})

$("#bot3").on('click', function(){
	x = x+1;
	console.log(2)
	if(x%2 == 0){
		console.log(0)
	$("#down3").attr('class', 'fa fa-caret-square-o-down');
}
else{
	console.log(1)
	$("#down3").attr('class', 'fa fa-caret-square-o-up');
}

})
$("#bot4").on('click', function(){
	x = x+1;
	console.log(2)
	if(x%2 == 0){
		console.log(0)
	$("#down4").attr('class', 'fa fa-caret-square-o-down');
}
else{
	console.log(1)
	$("#down4").attr('class', 'fa fa-caret-square-o-up');
}

})

