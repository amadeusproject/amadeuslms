/*
 * Copyright 2008, 2009 UFPE - Universidade Federal de Pernambuco
 *
 * Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 * 
 * O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como
 * publicada pela Fundação do Software LiveditMaterialRequestActivityre (FSF); na versão 2 da Licença.
 * 
 * Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 *  
 * Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENCA.txt", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
 *
 */

function showInputloginOpenID() {
	$("#dInputLoginOpenID").toggle("drop");
	$("#remindPassword").toggle("drop");
	window.setTimeout(function() {
		$("#identifier").focus();
	}, 1000);
}

function requestGoogleOpenID(url) {
	window.open(url, "_self");
}

function requestAddNewGoogleOpenId(url) {
	window.open(url, "_self");
}

function deleteGoogleOpenId(url) {
	window.open(url, "_self");
}

function requestOpenID(url) {
	window.open(url+dwr.util.getValue("identifier"), "_self");
}
