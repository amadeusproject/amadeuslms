/*
*
* Function to subscribe (works for courses and subjects)
*
*/
function subscribe(elem, url, confirm_message) {
	alertify.confirm(confirm_message, function(){
		$.ajax({
			dataType: "json",
			url: url,
			success: function (data) {
				if (data.status == "ok") {
					elem.disabled(true);
					alertify.success(data.message);
				} else {
					alertify.error(data.message);
				}
			}
		});
	});
}