/*
 * Copyright 2008, 2009 UFPE - Universidade Federal de Pernambuco
 *
 * Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 * 
 * O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como
 * publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 * 
 * Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 *  
 * Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENCA.txt", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
 *
 */

function ajaxLoadingConfig(div, innerHTML) {
	document.getElementById(div).innerHTML = innerHTML;
  	document.getElementById(div).style.textAlign = "center";
  	document.getElementById(div).style.color = "#2f7445"; 
  	document.getElementById(div).style.fontWeight = "bolder";
}

  function saveModule(idModule, positionModule, ajaxLoading) {
	  
	    ajaxLoadingConfig("dynamic"+positionModule, ajaxLoading);
	  
	  	var name    = trim(dwr.util.getValue("name"));
	  	var desc    = trim(dwr.util.getValue("description"));
	  	var visible    = "false";
	  	if (dwr.util.getValue("visible") == "on"){
	  		visible    = "true";
	  	}
	  	UtilDWR.getInclude('/saveModule.do?method=saveModule&idModule='+idModule+'&nameModule='+name+'&descriptionModule='+desc+'&visibleModule='+visible,
	 		function(data) {
	  			if (data.indexOf(keyUserNotLogged) != -1){
					window.open(urlUserNotLogged, "_self");
				} else {
					dwr.util.setValue('module'+positionModule, data, { escapeHtml:false });
					if (data.indexOf(keyError) == -1) {
						showEditName(idModule);
					}
				}
	  		}
	  	);
  }

  function deleteModule(idModule, positionModule, ajaxLoading) {
	  
	  ajaxLoadingConfig("dynamic"+positionModule, ajaxLoading);
	  	
	  UtilDWR.getInclude('/module.do?method=deleteModule&idModule='+idModule,
 		function(data) {
		  	if (data.indexOf(keyUserNotLogged) != -1){
				window.open(urlUserNotLogged, "_self");
			} else {
				dwr.util.setValue('form', data, { escapeHtml:false });
			}
  		}
  	);
  }

  function showNewModule(idCourse, positionModule, ajaxLoading) {
	ajaxLoadingConfig("loading"+positionModule, ajaxLoading);
	UtilDWR.getInclude('/module.do?method=newModule&idCourse='+idCourse,
 		function(data) {
			if (data.indexOf(keyUserNotLogged) != -1){
				window.open(urlUserNotLogged, "_self");
			} else {
				hideEditName(true,positionModule);
				dwr.util.setValue('module'+positionModule, data, { escapeHtml:false });
				execScript(data);
			}
  		}
  	);
  }
  
  function editModule(idModule, positionModule) {
	  UtilDWR.getInclude('/module.do?method=showViewEditModule&idModule='+idModule,
 		function(data) {
		  	if (data.indexOf(keyUserNotLogged) != -1){
				window.open(urlUserNotLogged, "_self");
			} else {
				hideEditName(false,positionModule);
				dwr.util.setValue('module'+positionModule, data, { escapeHtml:false });
				execScript(data);
			}
  		}
  	);  
  }
  
  function execScript(codigoHTMLcomScript) {
     var scriptObj = document.createElement('script');

     tmpScriptCode = codigoHTMLcomScript.split('<script type="text/javascript">');

     scriptCode = tmpScriptCode[1].split('</script>');

     scriptObj.setAttribute('language', 'javascript');

     scriptObj.text = scriptCode[0];

     document.body.appendChild(scriptObj);
  }
  
/*
	Trata a mudança de ordem dos módulos
*/  
	function changeOrder(idModule, positionModule, ajaxLoading){
		
		ajaxLoadingConfig("dynamic"+positionModule, ajaxLoading);
		
		var newValue = dwr.util.getValue('moduleNumber'+positionModule);
	
		UtilDWR.getInclude('/module.do?method=changeOrderModule&idModule='+idModule+'&oldPosition='+positionModule+'&newPosition='+newValue,
	 		function(data) {
				dwr.util.setValue('form', data, { escapeHtml:false });
				editModule(idModule, newValue);		
	  		}
	  	);
	}
  
  
  
/*
	Trata quando clica na opção de cancelar um módulo
*/
  function cancelModule(idModule,positionModule,ajaxLoading) {

	ajaxLoadingConfig("dynamic"+positionModule, ajaxLoading);
	
	UtilDWR.getInclude('/module.do?method=cancelModule&idModule='+idModule,
		function(data) {
			if (data.indexOf(keyUserNotLogged) != -1){
				window.open(urlUserNotLogged, "_self");
			} else {
				dwr.util.setValue('module'+positionModule, data, { escapeHtml:false });
				showEditName(idModule);
			}
		}
	);
  }

  function hideEditName(isNewModule, positionModule){
	var formAtual = dwr.util.getValue('form',{ escapeHtml:false });
	var iIndex = 1;
	var positionModule = 1;
	
	while (iIndex != -1){
		iIndex = formAtual.indexOf('editOption'+positionModule);
		if (iIndex != -1){
			dwr.util.setValue('editOption' + positionModule, trim('&nbsp;'),{ escapeHtml:false });
		}		
		positionModule++;
	}
	
	hideCreateNewModule(isNewModule, positionModule);
  }
  
  function showEditName(idModule){
	var formAtual = dwr.util.getValue('form', { escapeHtml:false });
	var iIndex = 1;
	var positionModule = 1;
	
	while (iIndex != -1){
		iIndex = formAtual.indexOf('editOption'+positionModule);
		if (iIndex != -1){
			var editLink = dwr.util.getValue('editLink' + positionModule, { escapeHtml:false });
			dwr.util.setValue('editOption' + positionModule, editLink ,{ escapeHtml:false });
		}		
		positionModule++;
	}
	
	UtilDWR.getInclude('/module.do?method=getIdCourseByIdModule&idModule='+idModule,
		function(data) {
			showCreateNewModule(trim(data) ,positionModule-1);
		}
	);
  }
  
/*
	Apaga a opção de criar novo módulo quando o modo esta em edição
*/
  function hideCreateNewModule(isNewModule, positionModule){ 
	  if(!isNewModule) {
		  var form = dwr.util.getValue('form',{ escapeHtml:false });
		  var iIndex = 1;
		  var lastPositionModule;
		  while (iIndex != -1){
			 iIndex = form.indexOf('module'+positionModule);
			 if (iIndex == -1){
				var start = form.lastIndexOf('<div');
				//O if abaixo é por causa do IE.
				if(start == -1) {
					start = form.lastIndexOf('<DIV');
				}
				var newForm = form.substring(0, start-3);
				dwr.util.setValue('form', newForm, { escapeHtml:false });
				lastPositionModule = (positionModule-1);
			 }
			 positionModule++;
		  }	  
	  }
  }
  
/*
	Re-escreve a opção de criar novo módulo quando o modo sai da edição
*/
  function showCreateNewModule(idCourse, lastPositionModule){
		UtilDWR.getInclude('/module.do?method=showViewClickNewModule&idCourse='+idCourse+'&lastPositionModule='+lastPositionModule,
			function(data) {
				var form = dwr.util.getValue('form',{ escapeHtml:false });
				dwr.util.setValue('form', form + data, { escapeHtml:false });
				execScript(data);
			}
		);
  }
  
  function makeUrl(name,order,desc,vis,idModuleBD){
  	msg = 'name='+ name + '&order=' + order + '&description=' + desc + '&visible=' + vis + '&idModuleBD='+idModuleBD;
  	return msg;
  }

 function trim(str) {
 	if (typeof str != 'string') {
 		return str;
 	}
	str = str.replace( /^\s+/g, '' );
	return str.replace( /\s+$/g, '' );
}
 
 function saveModulePressEnter(event,idModule, idModuleBD) {
	if (event.keyCode == 13) {
		saveModule(idModule,idModuleBD);
	}
 }