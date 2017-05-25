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