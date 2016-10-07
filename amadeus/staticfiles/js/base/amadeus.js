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
}

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
}

function validarCpfSemAlert(campo,nome,idElementoMensagemErro){
	//alert("teste");
	cpf = campo.value;

	cpf = cpf.replace(".","");
	cpf = cpf.replace("-","");
	cpf = cpf.replace(".","");
	retorno = true;
	
	if(trim(cpf).length > 0){
		//alert("teste2");
		cpfstr= '';
		temp = cpf + '';

		cpfstr = temp.substring(0,3);
		cpfstr = cpfstr + temp.substring(3,6);
		cpfstr = cpfstr + temp.substring(6,9);
		cpfstr = cpfstr + temp.substring(9,11);

		

		retorno = false;
		if(cpf != null){
			//alert("teste3");
			soma = 0;
			digito1 = 0;
			digito2 = 0;
			for(i = 0; i < 9; i = i + 1) {
				soma = soma + ((parseInt(cpf.substring(i,i+1)))*(11-(i+1)));
			}
			soma = soma % 11;
			if (soma == 0 || soma == 1) {
				digito1 = 0;
			} else {
				digito1 = 11 - soma;
			}
			soma = 0;

			for(i = 0; i < 9; i = i + 1) {
				soma = soma + ((parseInt(cpf.substring(i,i+1)))*(12-(i+1)));
			}
			soma = soma + (digito1*2);
			soma = soma % 11;
			if (soma == 0 || soma == 1) {
				digito2 = 0;
			}
			else{
				digito2 = 11 - soma;
			}
			digito = digito1 +''+ digito2;
			
			
			//alert(cpfstr.substring(9,11));
			if(digito == (cpfstr.substring(9,11))){
				retorno = true;
			} else{
				//alert("teste4");
				retorno = false;

			}
		} else {
			retorno = false;
		}
	}else{
		retorno = false;
	}
	//alert(retorno);
	if(retorno == false){
		//alert('E-mail informado invalido! Por favor, especifique um E-mail válido para o campo \"' + nome + '\".');
		document.getElementById(idElementoMensagemErro).style.display = '';
		campo.focus();
		return false;
	}else{
		document.getElementById(idElementoMensagemErro).style.display = 'none';
		return true;
	}
	return retorno;
}