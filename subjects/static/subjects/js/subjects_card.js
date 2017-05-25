/*
Function to open modal for subscribing to subject
**/

var open_modal = {
	get: function(url, id_modal, id_div_modal){
		$.get(url, function(data){
			if($(id_modal).exists()){ //So we check if does exist such modal
				$(id_div_modal).empty();
				$(id_div_modal).append(data);
			}else{
				$(id_div_modal).append(data);
			}
			$(id_modal).modal('show');
		});
	}
}


