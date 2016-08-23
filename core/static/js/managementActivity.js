/*
 * Copyright 2008, 2009 UFPE - Universidade Federal de Pernambuco
 *
 * Este arquivo � parte do programa Amadeus Sistema de Gest�o de Aprendizagem, ou simplesmente Amadeus LMS
 * 
 * O Amadeus LMS � um software livre; voc� pode redistribui-lo e/ou modifica-lo dentro dos termos da Licen�a P�blica Geral GNU como
 * publicada pela Funda��o do Software LiveditMaterialRequestActivityre (FSF); na vers�o 2 da Licen�a.
 * 
 * Este programa � distribu�do na esperan�a que possa ser �til, mas SEM NENHUMA GARANTIA; sem uma garantia impl�cita de ADEQUA��O a qualquer MERCADO ou APLICA��O EM PARTICULAR. Veja a Licen�a P�blica Geral GNU para maiores detalhes.
 *  
 * Voc� deve ter recebido uma c�pia da Licen�a P�blica Geral GNU, sob o t�tulo "LICENCA.txt", junto com este programa, se n�o, escreva para a Funda��o do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
 *
 */

//VARI�VEIS GLOBAIS
var gDynamicOption = ''; //Internacionaliza��o
var gEditOption = ''; //Internacionaliza��o
var editToolTip = 'Editar';
var removeToolTip = 'Remover';
var gIdEditModule = -1;//Essa vari�vel so recebe valor em "showListActivity()", "editActivity()" e "showActivity()". by Vinicius P�dua
var MMgameURL = "" //Vari�vel do endere�o do MM de Jogos, parametrizado! package br.ufpe.cin.amadeus.amadeus_game
var lastMaterial = null //Usada nos materiais acessados pelo professor

function ajaxLoadingConfig(div, innerHTML) {
	document.getElementById(div).innerHTML = innerHTML;
  	document.getElementById(div).style.textAlign = "center";
  	document.getElementById(div).style.color = "#2f7445"; 
  	document.getElementById(div).style.fontWeight = "bolder";
}

function eraseAndWriteNameActivity(moduleId, modulePosition) {
	cancelShowListMaterial(modulePosition);
	UtilDWR.getInclude('/module.do?method=eraseAndWriteNameActivity&moduleId='+moduleId,
 		function(data) {
 			
  		}
  	);
}

function showListActivity(idModule, positionModule) {
	UtilDWR.getInclude('/fListActivities.do?idModule='+idModule+'&positionModule='+positionModule,
 		function(data) {
 			if (gDynamicOption == ''){
				gDynamicOption = dwr.util.getValue('dynamic'+positionModule, { escapeHtml:false });
			}
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
  		}
  	);
}

function showListMaterial(idModule, positionModule) {
	UtilDWR.getInclude('/fListMaterials.do?idModule='+idModule+'&positionModule='+positionModule,
 		function(data) {
 			if (gDynamicOption == ''){
				gDynamicOption = dwr.util.getValue('dynamic'+positionModule, { escapeHtml:false });
			}
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}


function cancelShowListActivity(positionModule) {
	dwr.util.setValue('dynamic'+positionModule, gDynamicOption, { escapeHtml:false });
	gDynamicOption = '';
}


function cancelShowListMaterial(positionModule){
	dwr.util.setValue('dynamic'+positionModule, gDynamicOption, { escapeHtml:false });
	gDynamicOption = '';
}

function selectActivity(idModule, positionModule) {
	var select = dwr.util.getValue('activities'+positionModule, gDynamicOption, { escapeHtml:false });
	
	if (select != 'select'){
		switch(select){
			case 'game':
				showViewNewGameActivity(idModule, positionModule);
			break;
			case 'evaluation':
				showViewNewEvaluation(idModule, positionModule);
			break;
			case 'poll':
				newPoll(idModule, positionModule);
			break;
			case 'materialRequest':
				showViewNewMaterialRequestActivity(idModule, positionModule);
			break;
			case 'forum':
				showViewNewForumActivity(idModule, positionModule);
			break;
			case 'videoIriz':
				showViewYoutubeChooseVideoOrigin(idModule, positionModule);
			break;
			case 'learningObject':
				showViewNewLearningObject(idModule, positionModule);
			break;
			default:
			  alert("Sorry, wrong number to selectActivity");
			break;
		}
	}
}
// *** INICIO - ATIVIDADE JOGOS ***
function showViewNewGameActivity(moduleId, modulePosition){
	UtilDWR.getInclude('/gameActivity.do?method=showViewNewGameActivity&moduleId='+moduleId,
 		function(data) {
			dwr.util.setValue('dynamic'+modulePosition, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function createGame(moduleId, modulePosition){
	var name    = trim(dwr.util.getValue("nameGame"));
  	var description = trim(dwr.util.getValue("urlGame"));
  	var url = dwr.util.getValue("descriptionGame");

	UtilDWR.getInclude('/newGame.do?method=newGameActivity&nameGame='+name+'&urlGame='+description+'&descriptionGame='+url+'&moduleId='+moduleId,
 		function(data) {
			dwr.util.setValue('dynamic'+modulePosition, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
			 	cancelShowListActivity(modulePosition);
			 }
		}
  	);
}
function editGame(idActivity){
	UtilDWR.getInclude('/editGame.do?idModule='+gIdEditModule+'&idGame='+idActivity,
 		function(data) {
			dwr.util.setValue('dynamic'+gIdEditModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
			 }
		}
  	);	
	
}
function saveGame(idActivity){
	var name    = trim(dwr.util.getValue("nameGame"));
  	var url = trim(dwr.util.getValue("urlGame"));
  	var description = dwr.util.getValue("descriptionGame");


	UtilDWR.getInclude('/saveGame.do?method=saveGame&nameGame='+name+'&urlGame='+url+'&descriptionGame='+description+'&idGame='+idActivity+'&idModule='+gIdEditModule,
 		function(data) {
			dwr.util.setValue('dynamic'+gIdEditModule, data, { escapeHtml:false });
			
			 if (data.indexOf(keyError) != -1){
				dwr.util.setValue("nameGame",name);
			  	dwr.util.setValue("urlGame",url);
			  	dwr.util.setValue("descriptionGame",description);
			 }else{
			 	cancelShowListActivity(gIdEditModule);
			 }
		}
  	);
	
}

function deleteGame(idActivity){

	UtilDWR.getInclude('/deleteGame.do?method=deleteGame&idGame='+idActivity+'&idModule='+gIdEditModule,
 		function(data) {
		}
  	);
}

function logonMicroMundoJogos(idCourse,loginUser, path){
window.open(path+"/AmadeusGames/game/Prototipo.jsp?disciplina="+idCourse+"&login="+loginUser, " ", "width=800, height=600, directories=0, location=0, menubar=0, resizable=0, scrollbars=0, status=0"); 
}

function showGame(modulePosition, idActivity){
	UtilDWR.getInclude('/gameActions.do?method=showGame&idGame='+idActivity,
 		function(data) {
			dwr.util.setValue('editOption'+modulePosition, data, { escapeHtml:false });
  		}
  	);
}
function showPlayerGame(idMMJogos){

	UtilDWR.getInclude('/showPlayerGame.do?method=showPlayerGame&idMMJogos='+idMMJogos,
 		function(data) {
			dwr.util.setValue('optionGame'+gIdEditModule, data, { escapeHtml:false });
		}
  	);
}

function showScoreGame(type,idMMJogos){

	UtilDWR.getInclude('/changeOrderGame.do?method=changeOrderGame&type='+type+'&idMMJogos='+idMMJogos,
 		function(data) {
			dwr.util.setValue('optionGame'+gIdEditModule, data, { escapeHtml:false });
		}
  	);
}


// ***FIM - ATIVIDADE JOGOS ***

//*** INICIO - ATIVIDADE LEARNING OBJECTS ***
function showViewNewLearningObject(idModule, positionModule){
	UtilDWR.getInclude('/learningObject.do?method=showViewNewLearningObject&idModule='+idModule,
	 		function(data) {
				dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
				execScript(data);
	  		}
	);
}

function newLearningObjectActivity(idModule, positionModule, ajaxLoading){

	ajaxLoadingConfig('actions', ajaxLoading);
	
	var name = trim(dwr.util.getValue("nameLearningObject"));
  	var url = dwr.util.getValue("urlLearningObject");
  	var description = trim(dwr.util.getValue("descriptionLearningObject"));

  	UtilDWR.getInclude('/newLearningObject.do?method=newLearningObject&nameLearningObject='+name+'&urlLearningObject='+url+'&descriptionLearningObject='+description+'&idModule='+idModule,
  	 		function(data) {
  				dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
  				 if (data.indexOf(keyError) == -1){
  					cancelShowListActivity(positionModule);
  				 }
  			}
  	  	);
}


function showViewEditLearningObject(positionModule, idLearning){
	
	UtilDWR.getInclude('/learningObject.do?method=showViewEditLearningObject&idActivity='+idLearning,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
		}
  	);	
}


function editLearningObject(positionModule){
	
	var id = trim(dwr.util.getValue("idLearningObject"));
  	var name = trim(dwr.util.getValue("nameLearningObject"));
  	var url = trim(dwr.util.getValue("urlLearningObject"));
  	var description = trim(dwr.util.getValue("descriptionLearningObject"));
	
	UtilDWR.getInclude('/editLearningObject.do?method=editLearningObject&nameLearningObject='+name+'&urlLearningObject='+url+'&descriptionLearningObject='+description+'&idActivity='+id,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
				cancelShowListActivity(positionModule);
			 }
		}
  	);
}


function showViewLearningObjectActivity(positionModule, idActivity){
	
	UtilDWR.getInclude('/learningObject.do?method=showViewLearningObjectActivity&idActivity='+idActivity,
 		function(data) {
			dwr.util.setValue('editOption'+positionModule, data, { escapeHtml:false });
  		}
  	);
}	

function deleteLearningObjectActivity(idActivity){
	UtilDWR.getInclude('/learningObject.do?method=deleteLearningObjectActivity&idLearningObject='+idActivity,
	 		function(data) {
			}
	  	);
}

function openLearningObject(idActivity){
	
	UtilDWR.getInclude('/openLearningObject.do?method=openLearningObject&idLearningObject='+idActivity,
	 		function(data) {
			}
	  	);
}

function openLearningObjectNewWindow(url){
	window.open(url, '', 'width=600px, height=400px, directories=0, location=0, menubar=0, resizable=0, scrollbars=0, status=0');
}


//Atividades de HistoryLearningObject
function startSession(idActivity){
	UtilDWR.getInclude('/startSessionHistoryLearningObject.do?method=startSession&idLearningObject='+idActivity+'&idModule='+gIdEditModule,
 		function(data) {
		}
	);
}

function endSession(idHistory, score){
	UtilDWR.getInclude('/endSessionLearningObject.do?method=endSession&idHistory='+idHistory+'&score='+score,
	 		function(data) {
			}
	);
}

//***FIM - ATIVIDADE LEARNING OBJECTS ***

// *** INICIO - ATIVIDADE QUESTOES ***
var alfabeto = new Array();
alfabeto[0] = "a";alfabeto[1] = "b";alfabeto[2] = "c";alfabeto[3] = "d";alfabeto[4] = "e";alfabeto[5] = "f";alfabeto[6] = "g";alfabeto[7] = "h";alfabeto[8] = "i";alfabeto[9] = "j";alfabeto[10] = "k";alfabeto[11] = "l";alfabeto[12] = "m";alfabeto[13] = "n";alfabeto[14] = "o";alfabeto[15] = "p";

function addAlternative() {
	var id = $("#id").val();
	$("#alternatives_div").append("<div id='row" + id + "'>" + id + ") <input type='text' size='31' name='alternativesDescription' /> <input type='radio' name='alternativeCorrect' value='"+id+"' /><br/><br/></div>");
	
	id++;
	$("#id").val(id);
}

function addAlternativeTF() {
	var id = $("#idTF").val();
	$("#alternativesTF_div").append("<div id='rowTF" + id + "'>" + id + ")&nbsp;<input type='text' size='28' name='alternativesDescription' /> <input type='radio' name='alternativeCorrect"+(id-1)+"' value='true' />&nbsp;&nbsp;<input type='radio' name='alternativeCorrect"+(id-1)+"' value='false' checked='checked' /><br/><br/></div>");
	
	id++;
	$("#idTF").val(id);
}

function removeAlternativeTF() {
	var id = $("#idTF").val();
	if(id > 3){
		$("#rowTF" + (id - 1)).remove();
		id--;
		$("#idTF").val(id);
	}
}

function addAlternativeASS() {
	var id = $("#idASS").val();
	$("#alternativesASS_div").append("<div id='rowASS" + id + "'><div style='display:inline;margin-right:30px'>"+(1+parseInt(id))+") <input type='text' name='alternativesDescription' size='8'/></div><div style='display:inline;margin-right:10px'><input type='text' name='alternativesNumber' size='1'/></div><div style='display:inline'><input type='text' name='alternativesDescription2' size='13'/></div><br/><br/></div>");
	
	id++;
	$("#idASS").val(id);
}

function removeAlternative() {
	var id = $("#id").val();
	if(id > 3){
		$("#row" + (id - 1)).remove();
		id--;
		$("#id").val(id);
	}
}

function removeAlternativeASS() {
	var id = $("#idASS").val();
	$("#rowASS" + (id - 1)).remove();
	id--;
	$("#idASS").val(id);
}


var questionOptionTemp;

function showQuestions(idActivity){
	questionOptionTemp = $("#questionOption").clone();
	$("#questionOption").html("Carregando...");
	UtilDWR.getInclude('/fShowCreateQuestion.do?idModule='+gIdEditModule+'&idEvaluation='+idActivity,
 		function(data) {
			dwr.util.setValue('questionOption', data, { escapeHtml:false });
  		}
  	);
}

function cancelQuestions() {
	$("#questionOption").html(questionOptionTemp);
}

function submitForm(id, modulePosition) {
	var url = '/newQuestion.do?' + $("#" + id).serialize();
	UtilDWR.getInclude(url , function(data) {
		if (data.indexOf(keyError) == -1){
			dwr.util.setValue('dynamic'+modulePosition, data, { escapeHtml:false });
		} else {
			dwr.util.setValue('questionOption', data, { escapeHtml:false });
		}
  	});
}

function editSubmitForm(id, modulePosition, questionPosition) {
	var url = '/editQuestion.do?' + $("#" + id).serialize()+'&questionPosition='+questionPosition;
	UtilDWR.getInclude(url , function(data) {
		if (data.indexOf(keyError) == -1){
			dwr.util.setValue('dynamic'+modulePosition, data, { escapeHtml:false });
		} else {
			dwr.util.setValue('question'+questionPosition, data, { escapeHtml:false });
		}
  	});
}


function saveQuestionMultiple(modulePosition) {
	submitForm("form1", modulePosition);
}

function editQuestionMultiple(modulePosition, questionPosition) {
	editSubmitForm("form1", modulePosition, questionPosition);
}

function saveQuestionTrueFalse(modulePosition) {
	submitForm("form2", modulePosition);
}

function editQuestionTrueFalse(modulePosition, questionPosition) {
	editSubmitForm("form2", modulePosition, questionPosition);
}

function saveQuestionGap(modulePosition) {
	submitForm("form3", modulePosition);
}

function editQuestionGap(modulePosition, questionPosition) {
	editSubmitForm("form3", modulePosition, questionPosition);
}

function saveQuestionDiscursive(modulePosition) {
	submitForm("form4", modulePosition);
}

function editQuestionDiscursive(modulePosition, questionPosition) {
	editSubmitForm("form4", modulePosition, questionPosition);
}

function saveQuestionAssociation(modulePosition) {
	submitForm("form5", modulePosition);
}

function selectQuestion(questionType, idEvaluation) {
	switch(questionType){
		case 'M':
			UtilDWR.getInclude('/questionsOpen.do?method=showViewNewQuestionMultiple&evaluationId='+ idEvaluation,
			 		function(data) {
						if(data != ''){
						dwr.util.setValue('questionOption', data, { escapeHtml:false });
						}
			  		}
			  	);
			break;
		case 'V':
			UtilDWR.getInclude('/questionsOpen.do?method=showViewNewQuestionTrueFalse&evaluationId='+ idEvaluation,
			 		function(data) {
						if(data != ''){
						dwr.util.setValue('questionOption', data, { escapeHtml:false });
						}
			  		}
			  	);
			break;
		case 'A':
			UtilDWR.getInclude('/questionsOpen.do?method=showViewNewQuestionAssociation&evaluationId='+ idEvaluation,
			 		function(data) {
						if(data != ''){
						dwr.util.setValue('questionOption', data, { escapeHtml:false });
						}
			  		}
			  	);
			break;
		case 'P':
			UtilDWR.getInclude('/questionsOpen.do?method=showViewNewQuestionGap&evaluationId='+ idEvaluation,
			 		function(data) {
						if(data != ''){
						dwr.util.setValue('questionOption', data, { escapeHtml:false });
						}
			  		}
			  	);
			break;
		case 'D':
			UtilDWR.getInclude('/questionsOpen.do?method=showViewNewQuestionDiscursive&evaluationId='+ idEvaluation,
			 		function(data) {
						if(data != ''){
						dwr.util.setValue('questionOption', data, { escapeHtml:false });
						}
			  		}
			  	);
			break;
	}
}

function showViewDeleteConfirmationQuestion(modulePosition, evaluationId, questionId, questionPosition) {
	UtilDWR.getInclude('/questionsEvaluationActivity.do?method=showViewDeleteConfirmationQuestion&modulePosition='+modulePosition+'&evaluationId='+evaluationId+'&questionId='+ questionId,
 		function(data) {
			dwr.util.setValue('question'+questionPosition, data, { escapeHtml:false });
		}
  	);
}

function deleteQuestion(modulePosition, evaluationId, questionId) {
	UtilDWR.getInclude('/questionsEvaluationActivity.do?method=deleteQuestion&evaluationId='+evaluationId+'&questionId='+ questionId,
 		function(data) {
				dwr.util.setValue('dynamic'+modulePosition, data, { escapeHtml:false });
		}
  	);
}

function showViewEditQuestion(questionPosition, evaluationId, questionId) {
	UtilDWR.getInclude('/questionsEvaluationActivity.do?method=showViewEditQuestion&evaluationId='+evaluationId+'&questionId='+questionId+'&questionPosition='+questionPosition,
 		function(data) {
				dwr.util.setValue('question'+questionPosition, data, { escapeHtml:false });
		}
  	);
}


function cancelEditOption(positionModule) {
	backEditName(positionModule);
}

// ***FIM - ATIVIDADE QUESTOES ***

// *** INICIO - ATIVIDADE FORUM ***

function showViewNewForumActivity(idModule, positionModule){
	UtilDWR.getInclude('/forumActivity.do?method=showViewNewForumActivity&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function newForumActivity(idModule, positionModule, ajaxLoading){
	ajaxLoadingConfig('actions', ajaxLoading);
	
  	var topicForum = trim(dwr.util.getValue("topicForum"));
  	var descriptionForum = trim(dwr.util.getValue("descriptionForum"));
  	
  	UtilDWR.getInclude('/newForumActivity.do?method=newForumActivity&topicForum='+topicForum+'&descriptionForum='+descriptionForum+'&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			if (data.indexOf(keyError) == -1){
				cancelShowListActivity(positionModule);
			}
		}
  	);
}

function showViewEditForumActivity(positionModule, idForum){
	UtilDWR.getInclude('/forumActivity.do?method=showViewEditForumActivity&idForum='+idForum,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
		}
  	);	
}

function editForumActivity(positionModule, ajaxLoading){
	ajaxLoadingConfig('actions', ajaxLoading);
	
	var id = trim(dwr.util.getValue("idForum"));
	var topic = trim(dwr.util.getValue("nameForum"));
  	var description = trim(dwr.util.getValue("descriptionForum"));

	UtilDWR.getInclude('/editForumActivity.do?method=editForumActivity&idForum='+id+'&topicForum='+topic+'&descriptionForum='+description,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			if (data.indexOf(keyError) == -1){
				cancelShowListActivity(positionModule);
			}
		}
  	);
	
}

function deleteForumActivity(idForum){
	UtilDWR.getInclude('/forumActivity.do?method=deleteForumActivity&idForum='+idForum,
 		function(data) {
		}
  	);
}

function showViewForumActivity(positionModule, idForum){
	UtilDWR.getInclude('/forumActivity.do?method=showViewForumActivity&idForum='+idForum,
 		function(data) {
			dwr.util.setValue('editOption'+positionModule, data, { escapeHtml:false });
  		}
  	);
}

function showViewListMessagesForumActivity(positionModule, idForum){
	UtilDWR.getInclude('/forumActivity.do?method=showViewListMessagesForumActivity&idForum='+idForum,
 		function(data) {
			dwr.util.setValue('showRolagem'+positionModule, data, { escapeHtml:false });
			
			if (data.indexOf(keyError) != -1){
				//dwr.util.setValue("pagina",pagina);
			  	//dwr.util.setValue("idForum",idForum);
			} else {
				cancelShowListActivity(positionModule);
			}
		}
  	);
	
}

function showViewListMessagesForumActivity(positionModule, pagina, idForum){

	UtilDWR.getInclude('/forumActivity.do?method=showViewListMessagesForumActivity&idForum='+idForum+'&pagina='+pagina,
 		function(data) {
			dwr.util.setValue('showRolagem'+positionModule, data, { escapeHtml:false });
			
			if (data.indexOf(keyError) != -1){
				dwr.util.setValue("pagina",pagina);
			  	dwr.util.setValue("idForum",idForum);
			} else {
				cancelShowListActivity(positionModule);
			}
		}
  	);
	
}

function answerForumActivity(positionModule, idForum, idPerson){
	var body = trim(dwr.util.getValue("answerBody"));

	UtilDWR.getInclude('/answerForumActivity.do?method=answerForumActivity&answerBody='+body+'&idForum='+idForum,
		function(data) {
			if (data.indexOf(keyUserNotLogged) != -1){
				window.open(urlUserNotLogged, "_self");
			} else if (data.indexOf(keyError) != -1){
			  	dwr.util.setValue('answer'+positionModule, data, { escapeHtml:false });
			}else{
				dwr.util.setValue('answer'+positionModule, '', { escapeHtml:false });
				showViewListMessagesForumActivity(positionModule, 1, idForum);
			}
		}
  	);
	
}

function showViewNewAnswerForumActivity(positionModule, idForum){
	UtilDWR.getInclude('/forumActivity.do?method=showViewNewAnswerForumActivity&idForum='+idForum,
 		function(data) {
			dwr.util.setValue('answer'+positionModule, data, { escapeHtml:false });
  		}
  	);
}

function cancelShowAnswerForumActivity(positionModule){
	dwr.util.setValue('answer'+positionModule, '', { escapeHtml:false });
}

// *** FIM - ATIVIDADE FORUM ***


// *** INICIO - ATIVIDADE ENTREGA DE MATERIAL ***
function showViewNewMaterialRequestActivity(idModule, positionModule){
	UtilDWR.getInclude('/materialActivity.do?method=showViewNewMaterialRequestActivity&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function newMaterialRequestActivity(idModule, positionModule, ajaxLoading){
	ajaxLoadingConfig('actions', ajaxLoading);
	
  	var name = trim(dwr.util.getValue("nameMaterial"));
  	var day = trim(dwr.util.getValue("dayMaterial"));
  	var month = trim(dwr.util.getValue("monthMaterial"));
  	var year = trim(dwr.util.getValue("yearMaterial"));
  	var allow = dwr.util.getValue("allowMaterial");
  	var description = trim(dwr.util.getValue("descriptionMaterial"));
	
	UtilDWR.getInclude('/newMaterialRequestActivity.do?method=newMaterialRequestActivity&nameMaterial='+name+'&dayMaterial='+day+'&monthMaterial='+month+'&yearMaterial='+year+'&allowMaterial='+allow+'&idModule='+idModule+'&descriptionMaterial='+description,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
			 	cancelShowListActivity(positionModule);
			 }
		}
  	);
}

function editMaterialRequestActivity(positionModule, idActivity){
  	var name = trim(dwr.util.getValue("nameMaterial"));
  	var day = trim(dwr.util.getValue("dayMaterial"));
  	var month = trim(dwr.util.getValue("monthMaterial"));
  	var year = trim(dwr.util.getValue("yearMaterial"));
  	var allow = dwr.util.getValue("allowMaterial");
  	var description = trim(dwr.util.getValue("descriptionMaterial"));
	
	UtilDWR.getInclude('/editMaterialRequestActivity.do?method=editMaterialRequestActivity&nameMaterial='+name+'&dayMaterial='+day+'&monthMaterial='+month+'&yearMaterial='+year+'&allowMaterial='+allow+'&descriptionMaterial='+description+'&idActivity='+idActivity,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
			 	cancelShowListActivity(positionModule);
			 }
		}
  	);
}

function showViewEditMaterialRequestActivity(positionModule, idActivity){
	UtilDWR.getInclude('/materialActivity.do?method=showViewEditMaterialRequestActivity&idActivity='+idActivity,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
		}
  	);	
}

function deleteMaterialRequestActivity(idActivity){
	UtilDWR.getInclude('/materialActivity.do?method=deleteMaterialRequestActivity&idActivity='+idActivity,
 		function(data) {
		}
  	);
}

function showViewMaterialRequestActivity(positionModule, idActivity, callFromPaddingTask){
	UtilDWR.getInclude('/materialActivity.do?method=showViewMaterialRequestActivity&idActivity='+idActivity+'&callFromPaddingTask='+callFromPaddingTask,
		function(data) {
		dwr.util.setValue('editOption'+positionModule, data, { escapeHtml:false });
		execScript(data);
	}
	);	
}

function saveMaterialGrade(msgPosition, materialId, msgSuccess){
		var materialGrade = trim(dwr.util.getValue("materialGrade"+msgPosition));
		UtilDWR.getInclude('/materialActivity.do?method=saveMaterialGrade&materialId='+materialId+'&materialGrade='+materialGrade,
 		function(data) {
			if (data.indexOf(keyError) == -1){
				$("#msgMatInfo"+msgPosition).html(msgSuccess);
				$("#msgMatInfo"+msgPosition).toggle("drop"); 
				window.setTimeout(function() {
			   	 	$("#msgMatInfo"+msgPosition).toggle("drop");
			    }, 3000);
			}
		}
  	);	
}

function showMaterialRequestTeacher(positionModule, idActivity){
	UtilDWR.getInclude('/materialActivity.do?method=showMaterialRequestTeacher&idActivity='+idActivity,
		function(data) {
		dwr.util.setValue('editOption'+positionModule, data, { escapeHtml:false });
		execScript(data);
	}
	);	
}

// *** FIM - ATIVIDADE ENTREGA DE MATERIAL ***


// ** IN�CIO - ATIVIDADE MATERIAL ***

function showViewNewMaterialActivity(idModule, positionModule, ajaxLoading){
	
	ajaxLoadingConfig('actions', ajaxLoading);
	
	UtilDWR.getInclude('/materialActivity.do?method=showViewNewMaterialActivity&idModule='+idModule,
 		function(data) {
			if (gDynamicOption == ''){
				gDynamicOption = dwr.util.getValue('dynamic'+positionModule, { escapeHtml:false });
			}
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function createMaterial(idModule){
  	var name = trim(dwr.util.getValue("nameMaterial"));
	
	UtilDWR.getInclude('/newMaterial.do?method=newMaterial&nameMaterial='+name+'&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+gIdEditModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
			 	//addNewNameActivity('material',3,name);//USANDO REVERSEAJAX
				cancelShowListActivity(gIdEditModule);
			 }
		}
  	);
}

function showViewEditMaterialActivity(positionModule, idMaterial){
	UtilDWR.getInclude('/materialActivity.do?method=showViewEditMaterialActivity&idMaterial='+idMaterial,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
  		}
  	);	
}

function editMaterialChange(){
document.getElementById('showFile').style.display = "NONE";
document.getElementById('editFile').style.display = "BLOCK";
}

function deleteMaterialActivity(idActivity){
	UtilDWR.getInclude('/materialActivity.do?method=deleteMaterialActivity&idActivity='+idActivity,
 		function(data) {
		}
  	);
}

// *** FIM - ATIVIDADE MATERIAL ***


// *** IN�CIO - ATIVIDADE LINK EXTERNO ***
function showViewNewExternalLinkActivity(idModule, positionModule){
	UtilDWR.getInclude('/externalLink.do?method=showViewNewExternalLink&idModule='+idModule,
	 		function(data) {
				if (gDynamicOption == ''){
					gDynamicOption = dwr.util.getValue('dynamic'+positionModule, { escapeHtml:false });
				}
				dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
				execScript(data);
	  		}
	  	);
}

function newExternalLinkActivity(idModule, positionModule, ajaxLoading){
	ajaxLoadingConfig('actions', ajaxLoading);
	
  	var nameExternalLink = trim(dwr.util.getValue("nameExternalLink"));
  	var urlExternalLink = trim(dwr.util.getValue("urlExternalLink"));
  	var descriptionExternalLink = trim(dwr.util.getValue("descriptionExternalLink"));
  	
  	UtilDWR.getInclude('/newExternalLink.do?method=newExternalLink&nameExternalLink='+nameExternalLink+'&urlExternalLink='+urlExternalLink+'&descriptionExternalLink='+descriptionExternalLink+'&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			if (data.indexOf(keyError) == -1){
				cancelShowListActivity(positionModule);
			}
		}
  	);
}

function showViewExternalLinkActivity(positionModule, idActivity){
	UtilDWR.getInclude('/externalLink.do?method=showViewExternalLink&idExternalLink='+idActivity,
 		function(data) {
			dwr.util.setValue('editOption'+positionModule, data, { escapeHtml:false });
  		}
  	);
}	

function showViewEditExternalLink(positionModule, idExternalLink){
	UtilDWR.getInclude('/externalLink.do?method=showViewEditExternalLink&idExternalLink='+idExternalLink,
 		function(data) {
			if (gDynamicOption == ''){
				gDynamicOption = dwr.util.getValue('dynamic'+positionModule, { escapeHtml:false });
			}
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
		}
  	);	
}

function deleteExternalLink(idActivity){
	UtilDWR.getInclude('/externalLink.do?method=deleteExternalLink&idExternalLink='+idActivity,
	 		function(data) {
			}
	  	);
}

function editExternalLinkActivity(positionModule, ajaxLoading){
	ajaxLoadingConfig('actions', ajaxLoading);
	
	var id = trim(dwr.util.getValue("idExternalLink"));
	var name = trim(dwr.util.getValue("nameExternalLink"));
	var url = trim(dwr.util.getValue("urlExternalLink"));
  	var description = trim(dwr.util.getValue("descriptionExternalLink"));

	UtilDWR.getInclude('/editExternalLink.do?method=editExternalLink&idExternalLink='+id+'&nameExternalLink='+name+'&urlExternalLink='+url+'&descriptionExternalLink='+description,
		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
		 if (data.indexOf(keyError) == -1){
		 	cancelShowListActivity(positionModule);
		 }
		}
  	);
}


//*** FIM - ATIVIDADE LINK EXTERNO ***





// *** IN�CIO - ATIVIDADE ENQUETE ***
function newPoll(idModule, positionModule){
	UtilDWR.getInclude('/poll.do?method=showViewNewPoll&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function createPoll(idModule, positionModule,  ajaxLoading){
	
	ajaxLoadingConfig('actions', ajaxLoading);

  	var name = trim(dwr.util.getValue("namePoll"));
  	var question = trim(dwr.util.getValue("questionPoll"));
  	var day = trim(dwr.util.getValue("dayPoll"));
  	var month = trim(dwr.util.getValue("monthPoll"));
  	var year = trim(dwr.util.getValue("yearPoll"));
	var option = new Array();
	
	var iAnswer = 1;
	var form = dwr.util.getValue('poll_alt',{ escapeHtml:false });
	var iIndex = form.indexOf('alt'+'_'+iAnswer);
	while ( (iIndex != -1) ){
		option[iAnswer] = dwr.util.getValue('alt'+'_'+iAnswer);
		iAnswer++;
		iIndex = form.indexOf('alt'+'_'+iAnswer);
	}

	UtilDWR.getInclude('/newPoll.do?method=newPoll&namePoll='+name+'&questionPoll='+question+ makeOptions(option,iAnswer) +'&dayPoll='+day+'&monthPoll='+month+'&yearPoll='+year+'&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
			 	cancelShowListActivity(positionModule);
			 }else{
			 	dwr.util.removeAllOptions('poll_alt');
			 	for(var i=1 ; i < iAnswer ; i++){
			 		var form = '<input id=alt'+'_'+i+' type=text value = "'+option[i]+'"/>';
					if ( iAnswer > 3)
						form += ' [<a onclick=delAnswerPoll('+i+') href=javascript:void(0)>X</a>]';
			 		if (i>2){
						dwr.util.addOptions('poll_alt', [form], { escapeHtml:false });
			 		}else{
						dwr.util.addOptions('poll_alt', [form], { escapeHtml:false });
			 		}
			 	}
			 }
		}
  	);
}

function makeOptions(option,size){
	var result = '';
	for (var i = 1 ; i < size ; i++) {
		result += '&optionsPoll=' + option[i]; 
	}
	return result;
}

function newAnswerPoll(){
var iIndex = 1;
var iAnswer = 0;

	var form = dwr.util.getValue('poll_alt',{ escapeHtml:false });
	while ( (iIndex != -1) ){
		iAnswer++;
		var iIndex = form.indexOf('alt'+'_'+iAnswer);
	}
	
	var backup = new Array();
	
	for (var i = 1; i < iAnswer; i++) {
			backup[i] = dwr.util.getValue('alt'+'_'+i);
	}
	dwr.util.removeAllOptions('poll_alt');
	
	for (var i = 1; i < backup.length; i++) {
		var form = '<input id=alt'+'_'+i+' type=text value = "'+backup[i]+'"/> [<a onclick=delAnswerPoll('+i+') href=javascript:void(0)>X</a>]';
		dwr.util.addOptions('poll_alt', [form], { escapeHtml:false });
	}
	var form = '<input id=alt'+'_'+iAnswer+' type=text value = ""/> [<a onclick=delAnswerPoll('+iAnswer+') href=javascript:void(0)>X</a>]';
	dwr.util.addOptions('poll_alt', [form], { escapeHtml:false });
}

function delAnswerPoll(idDel){
var iIndex = 1;
var iAnswer = 0;

	var form = dwr.util.getValue('poll_alt',{ escapeHtml:false });
	while ( (iIndex != -1) ){
		iAnswer++;
		var iIndex = form.indexOf('alt'+'_'+iAnswer);	
	}
	
	var backup = new Array();
	
	for (var i = 1, j = 1; i < iAnswer; i++) {
		if (i != idDel) {
			backup[j] = dwr.util.getValue('alt'+'_'+i);
			j++;
		}
	}
	dwr.util.removeAllOptions('poll_alt');
	
	for (var i = 1; i < backup.length; i++) {
		var form = '<input id=alt'+'_'+i+' type=text value = "'+backup[i]+'"/>';
		if ( (backup.length-1) > 2)
			form += ' [<a onclick=delAnswerPoll('+i+') href=javascript:void(0)>X</a>]';
		dwr.util.addOptions('poll_alt', [form], { escapeHtml:false });
	}
}
function editPoll(positionModule, idActivity){
	UtilDWR.getInclude('/editPoll.do?idPoll='+idActivity,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
		}
  	);
}

function deletePoll(idPoll){
	UtilDWR.getInclude('/poll.do?method=deletePoll&idPoll='+idPoll,
 		function(data) {
		}
  	);
}

function showViewPollActivities(positionModule, idActivity){
	UtilDWR.getInclude('/fShowViewPoll.do?&idPoll='+idActivity,
 		function(data) {
			dwr.util.setValue('editOption'+positionModule, data, { escapeHtml:false });
  		}
  	);
}

function viewResultsPoll(idActivity, idModule){

	if (gEditOption == ''){
		gIdEditModule = idModule;
		gEditOption = dwr.util.getValue('editOption'+gIdEditModule, { escapeHtml:false });
	}
	
	UtilDWR.getInclude('/viewResultsPoll.do?idModule='+idModule+'&idPoll='+idActivity,
 		function(data) {
			dwr.util.setValue('editOption'+gIdEditModule, data, { escapeHtml:false });
		}
  	);	
}

function backViewResultsPoll(positionModule){
 	backEditName(positionModule);
}

function savePoll(idModule, positionModule, idActivity){
	
	var name = trim(dwr.util.getValue("namePoll"));
  	var question = trim(dwr.util.getValue("questionPoll"));
  	var day = trim(dwr.util.getValue("dayPoll"));
  	var month = trim(dwr.util.getValue("monthPoll"));
  	var year = trim(dwr.util.getValue("yearPoll"));
	var option = new Array();

	var iAnswer = 1;
	var form = dwr.util.getValue('poll_alt',{ escapeHtml:false });
	var iIndex = form.indexOf('alt'+'_'+iAnswer);
	while ( (iIndex != -1) ){
		option[iAnswer] = dwr.util.getValue('alt'+'_'+iAnswer);
		iAnswer++;
		iIndex = form.indexOf('alt'+'_'+iAnswer);
	}
	
	UtilDWR.getInclude('/savePoll.do?method=savePoll&namePoll='+name+'&questionPoll='+question+ makeOptions(option,iAnswer) +'&dayPoll='+day+'&monthPoll='+month+'&yearPoll='+year+'&idModule='+idModule+'&idPoll='+idActivity,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
			 	cancelShowListActivity(positionModule);
			 }else{
			 	dwr.util.removeAllOptions('poll_alt');
			 	for(var i=1 ; i < iAnswer ; i++){
			 		var form = '<input id=alt'+'_'+i+' type=text value = "'+option[i]+'"/>';
					if ( iAnswer > 3)
						form += ' [<a onclick=delAnswerPoll('+i+') href=javascript:void(0)>X</a>]';
			 		if (i>2){
						dwr.util.addOptions('poll_alt', [form], { escapeHtml:false });
			 		}else{
						dwr.util.addOptions('poll_alt', [form], { escapeHtml:false });
			 		}
			 	}
			 }
		}
  	);
	
}

function answerPoll(modulePosition, idActivity){
    
    var iIndex = 1;
	var iAnswer = 0;

	var name = trim(dwr.util.getValue("alternative"));
	var pollName = document.getElementById("pollName" + idActivity).innerHTML;
	
	var form = dwr.util.getValue('poll_alternative',{ escapeHtml:false });
	
	while ( (iIndex != -1) ){
		iAnswer++;
		var iIndex = form.indexOf('alternative'+'_'+iAnswer);
	}
	
	var backup = new Array();
	
	var idAlternative;
	
	for (var i = 1, j = 1; i < iAnswer; i++) {
		backup[j] = dwr.util.getValue('alternative'+'_'+i);
			
			if (backup[j] == true)
		 		idAlternative = i;
		j++;
	}
	
	UtilDWR.getInclude('/answerPoll.do?method=answerPoll&idAlternative='+idAlternative+'&idPoll='+idActivity,
		function(data) {
			if (data.indexOf(keyError) != -1 && data != ""){
			  	dwr.util.setValue('editOption'+modulePosition, data, { escapeHtml:false });
			} else {
			  	backEditName(modulePosition);
			  	document.getElementById("pollNamePlace" + idActivity).innerHTML = pollName;
			}
		}
  	);
}

// *** FIM - ATIVIDADE ENQUETE ***

// *** INICIO - ATIVIDADE EVALUATION ***
function showViewNewEvaluation(idModule, positionModule){
	UtilDWR.getInclude('/evaluation.do?method=showViewNewEvaluation&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function showViewEditEvaluation(positionModule, idEvaluation) {
	UtilDWR.getInclude('/evaluation.do?method=showViewEditEvaluation&evaluationId='+idEvaluation,
	 	function(data) {
	 		dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
	 		execScript(data);
		}
	);
}

function showViewEvaluationActivity(modulePosition, evaluationId, callFromPaddingTask){
	UtilDWR.getInclude('/evaluation.do?method=showViewEvaluationActivity&evaluationId='+evaluationId+'&callFromPaddingTask='+callFromPaddingTask,
 		function(data) {
			dwr.util.setValue('editOption'+modulePosition, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function deleteEvaluation(idEvaluation){
	UtilDWR.getInclude('/evaluation.do?method=deleteEvaluation&idEvaluation='+idEvaluation,
 		function(data) { }
  	);
}

function createEvaluation(idModule, positionModule, ajaxLoading){
	ajaxLoadingConfig('actions', ajaxLoading);
	
  	var descriptionEvaluation = trim(dwr.util.getValue("descriptionEvaluation"));
  	var startEvaluation = trim(dwr.util.getValue("startEvaluation"));
  	var finishEvaluation = trim(dwr.util.getValue("finishEvaluation"));
  	var afterdeadlineachievedEvaluation = trim(dwr.util.getValue("afterdeadlineachievedEvaluation"));
  	
	UtilDWR.getInclude('/newEvaluation.do?method=newEvaluation&descriptionEvaluation='+descriptionEvaluation+'&startEvaluation='+startEvaluation+'&finishEvaluation='+finishEvaluation+'&afterdeadlineachievedEvaluation='+afterdeadlineachievedEvaluation+'&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
				cancelShowListActivity(positionModule);
			 }
		}
  	);
}

function editEvaluation(idModule, positionModule, ajaxLoading){
	ajaxLoadingConfig('actions', ajaxLoading);
	
	var idEvaluation = trim(dwr.util.getValue("idEvaluation"));
	var descriptionEvaluation = trim(dwr.util.getValue("descriptionEvaluation"));
  	var startEvaluation = trim(dwr.util.getValue("startEvaluation"));
  	var finishEvaluation = trim(dwr.util.getValue("finishEvaluation"));
  	var afterdeadlineachievedEvaluation = trim(dwr.util.getValue("afterdeadlineachievedEvaluation"));
  	
	UtilDWR.getInclude('/editEvaluation.do?method=editEvaluation&descriptionEvaluation='+descriptionEvaluation+'&startEvaluation='+startEvaluation+'&finishEvaluation='+finishEvaluation+'&afterdeadlineachievedEvaluation='+afterdeadlineachievedEvaluation+'&idModule='+idModule+'&idEvaluation='+idEvaluation,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			 if (data.indexOf(keyError) == -1){
			 	cancelShowListActivity(positionModule);
			 }
		}
  	);
}

// *** FIM - ATIVIDADE EVALUATION ***

//Procedimento utilizado via ReverseAjax
function addNewNameActivity(type, positionModule, idActivity, nameActivity){
  	var activitiesList = nameActivity +' ' +
	'<a href=javascript:void(0) onclick=editActivity('+positionModule+',"'+type+'",'+idActivity+');><img src="themes/default/imgs/icons/pencil_small.png" class="editIcon" title='+editToolTip+'></a> ' +
	'<a href=javascript:void(0) onclick=deleteActivity("'+type+'",'+idActivity+');><img src="themes/default/imgs/icons/cross_small.png" class="editIcon" title='+removeToolTip+'></a>';
  	
  	if(type == 'material' || type == 'externalLink'){
  		dwr.util.addOptions('materialsList'+positionModule, [activitiesList], { escapeHtml:false });
  	}else {
  		dwr.util.addOptions('activitiesList'+positionModule, [activitiesList], { escapeHtml:false });
  	}
}


function addNewNameMaterial(positionModule, idActivity, nameActivity){
  	var activitiesList = nameActivity +' ' +
	'<a href=javascript:void(0) onclick=editActivity('+ positionModule + ',\'material\','+idActivity+');><img src="themes/default/themes/default/imgs/icons/pencil_small.png" class="editIcon" title='+editToolTip+'></a> ' +
	'<a href=javascript:void(0) onclick=deleteActivity(\'material\','+idActivity+');><img src="themes/default/imgs/icons/cross_small.png" class="editIcon" title='+removeToolTip+'></a>';
  	dwr.util.addOptions('materialsList'+positionModule, [activitiesList], { escapeHtml:false });
}

function removeAllNameActivity(positionModule){
  	dwr.util.removeAllOptions('activitiesList'+positionModule);
}

function removeAllNameMaterial(positionModule){
  	dwr.util.removeAllOptions('materialsList'+positionModule);
}

function editActivity(positionModule, type, idActivity) {
	
	if (gDynamicOption == ''){
		gDynamicOption = dwr.util.getValue('dynamic'+positionModule, { escapeHtml:false });
	}

	switch(type){
		case 'game':
			editGame(idActivity);
		break;
		case 'evaluation':
			showViewEditEvaluation(positionModule, idActivity);
		break;
		case 'poll':
			editPoll(positionModule, idActivity);
		break;
		case 'material':
			showViewEditMaterialActivity(positionModule, idActivity);
		break;
		case 'materialRequest':
			showViewEditMaterialRequestActivity(positionModule, idActivity);
		break;
		case 'forum':
			showViewEditForumActivity(positionModule, idActivity);
		break;
		case 'videoIriz':
			showViewEditVideoActivity(positionModule, idActivity);
		break;
		case 'learningObject':
			showViewEditLearningObject(positionModule, idActivity);
		break;
		case 'externalLink':
			showViewEditExternalLink(positionModule, idActivity);
		break;
		default:
		  alert("Sorry, wrong number to editActivity");
		break;
	}
}

function saveActivity(type,idActivity) { 
	//N�O PRECISA PEGAR O ID, POIS PARA ENTRAR AQUI JA ENTROU NA FUN��O QUE PEGA
	switch(type){
		case 'game':
			saveGame(idActivity);
		break;
		case 'studentEvaluation':
			alert('studentEvaluation'+idActivity);
		break;
		case 'evaluation':
			alert('evaluation'+idActivity);
		break;
		case 'poll':
			editPoll(idActivity);
		break;
		case 'material':
			editMaterial(idActivity);
		break;
		case 'forum':
			editForumActivity(idActivity);
		break;
		case 'videoIriz':
			saveVideoIriz(idActivity);
		break;
		default:
		  alert("Sorry, wrong number to saveActivity");
		break;
	}
}

function deleteActivity(type, idActivity) {
	switch(type){
		case 'game':
			deleteGame(idActivity);
		break;
		case 'evaluation':
			deleteEvaluation(idActivity);
		break;
		case 'poll':
			deletePoll(idActivity);
		break;
		case 'material':
			deleteMaterialActivity(idActivity);
		break;
		case 'materialRequest':
			deleteMaterialRequestActivity(idActivity);
		break;
		case 'forum':
			deleteForumActivity(idActivity);
		break;
		case 'videoIriz':
			deleteVideoIriz(idActivity);
		break;
		case 'learningObject':
			deleteLearningObjectActivity(idActivity);
		break;
		case 'externalLink':
			deleteExternalLink(idActivity);
		break;
		default:
		  alert("Sorry, wrong number to deleteActivity");
		break;
	}
}

	function showActivity(positionModule, type, idActivity) {	
		switch(type){
			case 'game':
				showGame(positionModule, idActivity);
			break;
			case 'evaluation':
				showViewEvaluationActivity(positionModule, idActivity, false);
			break;
			case 'poll':
				showViewPollActivities(positionModule, idActivity);
			break;
			case 'materialRequest':
				showViewMaterialRequestActivity(positionModule, idActivity, false);
			break;
			case 'materialRequestTeacher':
				showMaterialRequestTeacher(positionModule, idActivity);
			break;
			case 'forum':
				showViewForumActivity(positionModule, idActivity);
			break;
			case 'videoIriz':
				showVideoIriz(positionModule, idActivity);
			break;
			case 'learningObject':
				showViewLearningObjectActivity(positionModule, idActivity);
			break;
			case 'externalLink':
				showViewExternalLinkActivity(positionModule, idActivity);
			break;
			default:
			  alert("Sorry, wrong number to showActivity");
			break;
		}
	}

  function backEditName(positionModule){
	var editLink = dwr.util.getValue("editLink"+positionModule, { escapeHtml:false } );
  	dwr.util.setValue('editOption'+positionModule, editLink, { escapeHtml:false });
  }
  
  // ****************** IRIZ **************************
    
  function getVideoURL(codigoHTMLcomScript)
  {
  
	var videoID;

    var tmpScriptCode1 = codigoHTMLcomScript.split('var watchMapUrl =');
    
    var tmpScriptCode2 = tmpScriptCode1[1].split('var watchGamUrl =');

	tmpScriptCode1 = tmpScriptCode2[0].split('&video_id=');
	
	tmpScriptCode2 = tmpScriptCode1[1].split(';');
	
	videoID = "file:///C:/Users/Natanael/Documents/Flex Builder 3/Iriz/bin-debug/Iriz.html?videoUrl=" +  
			"http://www.youtube.com/get_video?video_id=" +  tmpScriptCode2[0] + "&login=loginTeste";
	alert(videoID);		
	window.location = videoID;
			
  }
  
  function showViewYoutubeChooseVideoOrigin(idModule, positionModule){
	UtilDWR.getInclude('/videoActivity.do?method=showViewYoutubeChooseVideoOrigin&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function showVideoIriz(positionModule, idActivity){	  
	  UtilDWR.getInclude('/showVideoIrizStatus.do?idActivity='+idActivity,
			function(data) {
		  		dwr.util.setValue('editOption'+positionModule, data, { escapeHtml:false });
  	  		}
	  );
}	

  function deleteVideoIriz(idActivity){
	UtilDWR.getInclude('/videoActivity.do?method=deleteVideoActivity&idActivity='+idActivity,
 		function(data) {
  		}
  	);
}

function showViewEditVideoActivity(modulePosition, videoId){	
	UtilDWR.getInclude('/videoActivity.do?method=showViewEditVideoActivity&videoId='+videoId,
	 	function(data) {
			dwr.util.setValue('dynamic'+modulePosition, data, { escapeHtml:false });
  		}
  	);
}

function editVideoActivity(positionModule, idVideo){
	var id = trim(dwr.util.getValue("videoIrizId"));
	var name = trim(dwr.util.getValue("videoIrizName"));
	var desc = trim(dwr.util.getValue("videoDescription"));
	var url = trim(dwr.util.getValue("url"));
	
	UtilDWR.getInclude('/editVideoActivity.do?method=editVideoActivity&videoId='+id+'&videoIrizName='+name+'&videoDescription='+desc+'&url='+url,
	 	function(data) {
			dwr.util.setValue('dynamic'+positionModule, data, { escapeHtml:false });
			if (data.indexOf(keyError) == -1){
				cancelShowListActivity(positionModule);
			}
  		}
  	);
}
	
function watchVideo(url){
	window.open(url,'','width=800px, height=600px, directories=0, location=0, menubar=0, resizable=0, scrollbars=0, status=0');
}
  
function chooseFileOrigin(idModule){
	var name = trim(dwr.util.getValue("videoIrizName"));
	var desc = trim(dwr.util.getValue("videoDescription"));
	var choice = trim(dwr.util.getValue("choice"));
	
	UtilDWR.getInclude('/videoActivity.do?method=chooseFileOrigin&videoIrizName='+name+'&videoDescription='+desc+'&choice='+choice+'&idModule='+idModule,
 		function(data) {
			dwr.util.setValue('video', data, { escapeHtml:false });
			execScript(data);
  		}
  	);
}

function createVideoIriz(idModule){
var name = trim(dwr.util.getValue("videoIrizName"));
var desc = trim(dwr.util.getValue("videoDescription"));
var url = trim(dwr.util.getValue("url"));

	UtilDWR.getInclude('/newVideoIrizFromURL.do?method=newVideoIrizFromURL&idModule='+idModule+'&videoIrizName='+name+'&videoDescription='+desc+'&url='+url,
 		function(data) {
  		}
  	);
}

function uploadVideoIrizToYoutubeStep1(moduleId){
	var name = trim(dwr.util.getValue("nameVideoIriz"));
	var desc = trim(dwr.util.getValue("videoDescription"));
	var file = trim(dwr.util.getValue("file"));

	UtilDWR.getInclude('/newVideoIrizUploadStep1.do?moduleId='+moduleId+'&name='+name+'&desc='+desc,
 		function(data) {
  		}
  	);
}

// ****************** FIM DO IRIZ **************************


function execScript(codigoHTMLcomScript)
  {
     var scriptObj = document.createElement('script');

     tmpScriptCode = codigoHTMLcomScript.split('<script type="text/javascript">');

     scriptCode = tmpScriptCode[1].split('</script>');
    	 
	 scriptObj.setAttribute('language', 'javascript');
	 
	 scriptObj.text = scriptCode[0];
	 
	 document.body.appendChild(scriptObj); 
  }

function correctEvaluationRealized(id, modulePosition) {
	var url = '/evaluation.do?' + $("#" + id).serialize();

	UtilDWR.getInclude(url,	function(data) {
		dwr.util.setValue('editOption'+modulePosition, data, { escapeHtml:false });
		}
  	);
}

function saveRealizedEvaluation(position,isFromPaddingTask) {
	if(isFromPaddingTask == 1){
		var url = '/saveRealizedEvaluation.do?' + $("#realizedEvaluation"+position).serialize();
	}else{
		var url = '/saveRealizedEvaluation.do?' + $("#realizedEvaluation").serialize();
	}
	
	UtilDWR.getInclude(url , function(data) {
		dwr.util.setValue('editOption'+position, data, { escapeHtml:false });
	});
}

