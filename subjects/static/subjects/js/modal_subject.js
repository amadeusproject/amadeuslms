/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

var RemoveSubject = {
  remove: function(url,dados,id_li_link){
	$("#subject").modal('toggle');
	  $.post(url,dados, function(data){
		// $(id_li_link).remove();
		// $('body').removeClass('modal-open');
		// $("#modal_course").empty();
		// $(".modal-backdrop.in").remove();
		window.location.href = data['url'];
		//alertify.success("Subject removed successfully!");
	  }).fail(function(){
		$("#modal_course").empty();
		$("#modal_course").append(data);
		$('#subject').modal('show');
	  });
  }
}
var delete_subject = {
  get: function (url, id_modal, id_div_modal){
	$.get(url, function(data){
	  if($(id_modal).length){
		$(id_div_modal).empty();
	  }
	  if (!data['error']){ //If there is no error in the removing process, no message is shown
		$(id_div_modal).append(data);
		$(id_modal).modal('show');
	  }else{
		window.location.href = data['url']; // If there is a error, we redirect to another URL
	  }
	});
  }
};


var subscribe_subject = {
  get: function(url, id_modal, id_div_modal){
	$.get(url, function(data){
	  if($(id_modal).length){
		$(id_div_modal).empty();
	  }
	  if (!data['error']){ //If there is no error in the removing process, no message is shown
		$(id_div_modal).append(data);
		$(id_modal).modal('show');
	  }else{
		window.location.href = data['url']; // If there is a error, we redirect to another URL
	  }
	});
  }
}


var SubscribeSubject = {
  subscribe: function(url,dados,id_li_link){
	$("#subject").modal('toggle');
	  $.post(url,dados, function(data){
		$(id_li_link).remove();
		$('body').removeClass('modal-open');
		$("#modal_course").empty();
		$(".modal-backdrop.in").remove();
		window.location.href = data['url'];
	  }).fail(function(){
		$("#modal_course").empty();
		$("#modal_course").append(data);
		$('#subject').modal('show');
	  });
  }
}