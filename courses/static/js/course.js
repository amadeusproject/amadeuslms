/*
*
* Function to subscribe (works for courses and subjects)
*
*/
function subscribe(elem, url, id, confirm_message) {
	alertify.confirm(confirm_message, function(){
		$.ajax({
			dataType: "json",
			url: url,
			success: function (data) {
				if (data.status == "ok") {
					elem.remove();
					alertify.success(data.message);
					$(".panel_"+id).find(".view_btn").show()
				} else {
					alertify.error(data.message);
				}
			}
		});
	});
}