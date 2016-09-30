$(document).ready(function(){
	$('[data-toggle="tooltip"]').tooltip(); //activate tooltip on all elements that has attribute data-toggle
});


/*

*/
function getNotifications(step){
	$.ajax('/getNotifications',{
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