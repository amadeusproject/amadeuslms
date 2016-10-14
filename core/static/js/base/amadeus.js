function campoNumerico(campo, evento){
    var codTecla;
    var tamanho;
	
    if( document.all ) {// Internet Explorer
        codTecla = evento.keyCode;
    } else if( document.layers ) { // Nestcape
        codTecla = evento.which;
    }
    else if( evento) { // Firefox
        codTecla = evento.which;
    }
    if( (codTecla > 47 && codTecla < 58)  || codTecla==8  || codTecla == 0){
        return true;
    } else {
    	evento.returnValue = false;
  	    return false;
    }
};

function formatarCpf(campo, evento){
	var codTecla;
	var tamanho;
	if( document.all ) { // Internet Explorer
	codTecla = evento.keyCode;
	} else if( document.layers ) { // Nestcape
	codTecla = evento.which;
	}
	else if( evento ) { // Firefox
        codTecla = evento.which;
        }
	tamanho = campo.value.length;
	if( (codTecla > 47 && codTecla < 58)  || codTecla== 8 || codTecla == 0){
		if(tamanho < 14 ){
			if( tamanho == 3 && codTecla != 8 && codTecla != 0){
				campo.value = campo.value + ".";
			}else if( tamanho == 7 && codTecla != 8 && codTecla != 0){
				campo.value = campo.value + ".";
			}else if( tamanho == 11 && codTecla != 8 && codTecla != 0){
				campo.value = campo.value + "-";
			}
		}else{
			evento.returnValue = false;
		}
		return true;
	} else {
		return false;
	}
	return false;
};

function formatarTelefone(campo, evento){
	var codTecla;
	var tamanho;
	if( document.all ) { // Internet Explorer
		codTecla = evento.keyCode;
	} else if( document.layers ) { // Nestcape
		codTecla = evento.which;
	} else if( evento ) { // Firefox
   		codTecla = evento.which;
	}
	tamanho = campo.value.length;
	
	if(((codTecla > 47 && codTecla < 58) || (codTecla == 8)) && tamanho < 15){
	
		if(tamanho == 0){
			campo.value = "(" + campo.value;
		}else if( tamanho == 3 ){
			campo.value = campo.value + ") ";
		}else if(tamanho == 9){
			campo.value = campo.value + "-";
		}else if(tamanho == 14){
			// alert('oi');
			campo.value = campo.value.slice(0, 4) + campo.value.slice(5, 14);
			campo.value = campo.value.slice(0, 8) + campo.value.slice(9, 10) + campo.value.slice(8, 9) + campo.value.slice(10, 14)
		}
		return true;

	} else if(codTecla == 0 || codTecla == 8){
		return true;
	} else {
		evento.returnValue = false;
		return false;
	}
	return false;
}

/*
This functions get the next 5 notifications from the user given a "step"(an amount) of previous notifications
*/
function getNotifications(step){
	$.get('/getNotifications',
		{'steps':step, 'amount': 5}, function(data){
			$("#notification-dropdown").append(data);
			$('#notification-see-more').remove();
			var seemore = '<li><a onclick="getNotifications('+(step+5)+')"> <div id="notification-see-more" class="list-group-item"> <div class="row-content"><p class="list-group-item-text">See More</p> </div>  </a></li>';
			$("#notification-dropdown").append(seemore);
			$("#notification-count").text(step+5);
		});
}
