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

var msgCancel;
var msgApprove;

var lastRequest = null;

function ajaxLoadingConfig(div, innerHTML) {
	document.getElementById(div).innerHTML = innerHTML;
  	document.getElementById(div).style.textAlign = "center";
  	document.getElementById(div).style.color = "#2f7445"; 
  	document.getElementById(div).style.fontWeight = "bolder";
}

function init(approve, cancel) {
	msgCancel = cancel;
	msgApprove = approve;
	pinballEffect();
}

function showDetails(requestId) {
	if (lastRequest != null)
		hideDetails(lastRequest);
	lastRequest = requestId;
	
	document.getElementById('request'+requestId).className = "requestExpanded";
	document.getElementById('reqInfo'+requestId).style.display = "BLOCK";
	document.getElementById('reqBtns'+requestId).style.display = "BLOCK";
}

function hideDetails(requestId, innerHTML, msgSuccess) {
	document.getElementById('request'+requestId).className = "requestColapsed";
	document.getElementById('reqInfo'+requestId).style.display = "NONE";
	document.getElementById('reqJust'+requestId).style.display = "NONE";
	document.getElementById('reqBtns'+requestId).style.display = "NONE";

	document.getElementById('reqJustification'+requestId).value = '';
	document.getElementById('reqBtnLeft'+requestId).blur();
	document.getElementById('reqBtnLeft'+requestId).value = msgApprove;
	document.getElementById('reqBtnLeft'+requestId).onclick = function() {approveRequest(requestId, innerHTML, msgSuccess)};	
	document.getElementById('reqBtnRight'+requestId).onclick = function() {showJustBox(requestId, innerHTML, msgSuccess)};
}

function showJustBox(requestId, innerHTML, msgSuccess) {
	document.getElementById('reqInfo'+requestId).style.display = "NONE";
	document.getElementById('reqJust'+requestId).style.display = "BLOCK";

	document.getElementById('reqJustification'+requestId).focus();
	document.getElementById('reqBtnLeft'+requestId).value = msgCancel;
	document.getElementById('reqBtnLeft'+requestId).onclick = function() {showDetails(requestId, innerHTML, msgSuccess)};	
	document.getElementById('reqBtnRight'+requestId).onclick = function() {disaproveRequest(requestId, innerHTML, msgSuccess)};
}

function approveRequest(requestId, innerHTML, msgSuccess) {
	ajaxLoadingConfig("reqBtns"+requestId, innerHTML);
	var cb = {callback:function(data) {requestServerResponse(requestId, data);}};

	UtilDWR.getInclude('/approvedTeachingRequest.do?parameter=Aprovacao&userRequestId='+requestId,
 		function(data) {
 		dwr.util.setValue('request'+requestId, msgSuccess, { escapeHtml:false });
		document.getElementById('request'+requestId).className = "NONE";
		lastRequest = null;
  		}
  	);
}

function disaproveRequest(requestId, innerHTML, msgSuccess) {
	
	var just = document.getElementById('reqJustification'+requestId).value;
	var cb = {callback:function(data) {requestServerResponse(requestId, data);}};
	if (just == "") {alert("Você deve escrever uma justificativa");
	}else{
	ajaxLoadingConfig("reqBtns"+requestId, innerHTML);
	UtilDWR.getInclude('/disapprovedTeachingRequest.do?parameter=Reprovacao&userRequestId='+requestId+'&justification='+just,
 		function(data) {
 		dwr.util.setValue('request'+requestId, msgSuccess, { escapeHtml:false });
		document.getElementById('request'+requestId).className = "NONE";
		lastRequest = null;
  		}
  	);	

	}
}

function requestServerResponse(requestId, data) {
	if (data != null) {
		alert(data);
	} else {
		$('request'+requestId).style.display = 'none';
	}
}

// ## PinBall Effect ## //

var lastElement = null;
var W3CDOM = (document.createElement && document.getElementsByTagName);

function pinballEffect() {
	if (!W3CDOM) return;
	var allElements = document.getElementsByTagName('div');
	var originalBackgrounds=new Array();
	for (var i=0; i<allElements.length; i++) {
		if (allElements[i].className.indexOf('pinball-scoop') !=-1) {
			pinballAddEvents(allElements[i]);
		}
	}
}

function mouseGoesOver() {
	originalClassNameString = this.className;
	this.className += " pinball-on";
	this.style.cursor = "pointer";
	//this.style.cursor = "hand";
}

function mouseGoesOut() {
	this.className = originalClassNameString;
}

function mouseGoesClick() {
	var allThisAreasElements = this.getElementsByTagName('*');
	for (var j=0; j<allThisAreasElements.length; j++) {
		if (allThisAreasElements[j].className.indexOf('pinball-sinkhole') != -1) {
			if (lastElement != null)
				pinballAddEvents(lastElement);

			lastElement = this;
			allThisAreasElements[j].onclick();
			originalClassNameString = this.className;
			pinballRemoveEvents(this);
		}
	}
}

function pinballAddEvents(element) {
	element.onmouseover = mouseGoesOver;
	element.onmouseout = mouseGoesOut;
	element.onclick = mouseGoesClick;
}
function pinballRemoveEvents(element) {
	element.onmouseover = function() {};
	element.onmouseout = function() {};
	element.onclick = function() {};
	element.style.cursor = 'default';
}