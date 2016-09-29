$(document).ready(function(){
	$('[data-toggle="tooltip"]').tooltip(); //activate tooltip on all elements that has attribute data-toggle
});


/*

*/
function loadNotifications(step){
	$.ajax('/loadNotifications',{
		steps: step,
		amount: 5,
		sucess: function(response){

		}
	});
}


/*

*/
function checkIfNewNotification(){

} 