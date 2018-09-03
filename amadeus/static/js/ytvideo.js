/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

// Load the IFrame Player API code asynchronously.
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/player_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var keepAlive;
	
var player;
function onYouTubePlayerAPIReady() {
	player = new YT.Player('video');

	player.addEventListener("onStateChange", "onPlayerStateChange");	
}

function onPlayerStateChange(event) {
	switch (event.data) {
		case YT.PlayerState.UNSTARTED:
	  		console.log('unstarted');
	  		break;
		case YT.PlayerState.ENDED:
			clearInterval(keepAlive)
	  		
			watchLog("close");
	  		
	  		finishLog();
	  		break;
		case YT.PlayerState.PLAYING:
			keepAlive = setInterval(function () {
				keepLogged()
			}, 60000);
			
	  		watchLog("open");
	  		break;
		case YT.PlayerState.PAUSED:
			clearInterval(keepAlive)
	  		
	  		watchLog("close");
	  		break;
		case YT.PlayerState.BUFFERING:
	  		console.log('buffering');
	  		break;
		case YT.PlayerState.CUED:
	  		console.log('video cued');
	  	break;
  	}
}

function keepLogged () {
	$(document).mousemove();
}

function watchLog (action) {
	var url = $('#log_url').val();
    var log_input = $('#log_id');

	$.ajax({
        url: url,
        data: {'action': action, 'log_id': log_input.val()},
        dataType: 'json',
        success: function (data) {
        	if (action == "open") {
            	log_input.val(data.log_id);
        	}
        },
        error: function (data) {
            console.log(data);
        }
    });
}

function finishLog () {
	var url = $('#log_finish_url').val();

	$.ajax({
        url: url,
        dataType: 'json',
        success: function (data) {
        	console.log(data);
        },
        error: function (data) {
            console.log(data);
        }
    });
}