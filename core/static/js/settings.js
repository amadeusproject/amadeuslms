/*
 * Copyright 2008, 2009 UFPE - Universidade Federal de Pernambuco
 *
 * Este arquivo � parte do programa Amadeus Sistema de Gest�o de Aprendizagem, ou simplesmente Amadeus LMS
 * 
 * O Amadeus LMS � um software livre; voc� pode redistribui-lo e/ou modifica-lo dentro dos termos da Licen�a P�blica Geral GNU como
 * publicada pela Funda��o do Software Livre (FSF); na vers�o 2 da Licen�a.
 * 
 * Este programa � distribu�do na esperan�a que possa ser �til, mas SEM NENHUMA GARANTIA; sem uma garantia impl�cita de ADEQUA��O a qualquer MERCADO ou APLICA��O EM PARTICULAR. Veja a Licen�a P�blica Geral GNU para maiores detalhes.
 *  
 * Voc� deve ter recebido uma c�pia da Licen�a P�blica Geral GNU, sob o t�tulo "LICENCA.txt", junto com este programa, se n�o, escreva para a Funda��o do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
 *
 */

function saveWebSecuritySettings(){
	var url = "/settingsActions.do?method=saveWebSecuritySettings&"
	var autoSigning = dwr.util.getValue("autoSigning");
	UtilDWR.getInclude(url+"autoSigning="+autoSigning , 
	function(data) {
		if (data.indexOf(keyUserNotLogged) != -1){
			window.open(urlUserNotLogged, "_self");
		} else if (data.indexOf(keyAccessDenied) != -1) { 
			window.open(urlAccessDenied, "_self");
		} else {
			execScript(data);
			dwr.util.setValue("security", data, { escapeHtml:false });
		}
  	});
}

function saveWebMailSenderSettings(){
	var url = "/webSettingMailSender.do?method=saveWebMailSenderSettings&"+$("#formWebSettingMailSender").serialize();
	UtilDWR.getInclude(url, 
	function(data) {
		if (data.indexOf(keyUserNotLogged) != -1){
			window.open(urlUserNotLogged, "_self");
		} else if (data.indexOf(keyAccessDenied) != -1) { 
			window.open(urlAccessDenied, "_self");
		} else {
			execScript(data);
			dwr.util.setValue("mailSender", data, { escapeHtml:false });
		}
  	});
}

function saveSystemSettings(){
	var url = "/webSettingMailSender.do?method=saveWebMailSenderSettings&"+$("#formWebSettingMailSender").serialize();
	$("#imgMobile").show();
	UtilDWR.getInclude(url, 
	function(data) {
		if (data.indexOf(keyUserNotLogged) != -1){
			window.open(urlUserNotLogged, "_self");
		} else if (data.indexOf(keyAccessDenied) != -1) { 
			window.open(urlAccessDenied, "_self");
		} else {
			execScript(data);
			dwr.util.setValue("mailSender", data, { escapeHtml:false });
		}
		$("#imgMobile").show();
  	});
}

function sleep(milliseconds) {
	  var start = new Date().getTime();
	  for (var i = 0; i < 1e7; i++) {
	    if ((new Date().getTime() - start) > milliseconds){
	      break;
	    }
	  }
}

function saveMobileSettings(){
	var url = "/settingsActions.do?method=saveMobileSettings&"+$("#formMobileSetting").serialize();
	$("#imgMobile").show();
	
	UtilDWR.getInclude(url, 
	function(data) {
		if (data.indexOf(keyUserNotLogged) != -1){
			window.open(urlUserNotLogged, "_self");
		} else if (data.indexOf(keyAccessDenied) != -1) { 
			window.open(urlAccessDenied, "_self");
		} else {
			execScript(data);
		}
		$("#imgMobile").hide();
  	});
}
