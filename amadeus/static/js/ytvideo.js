// Load the IFrame Player API code asynchronously.
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/player_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
var keepAlive;
	// Replace the 'ytplayer' element with an <iframe> and
	// YouTube player after the API code downloads.
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
	  		console.log('ended');
	  		break;
		case YT.PlayerState.PLAYING:
			keepAlive = setInterval(function () {
				keepLogged()
			}, 60000);
	  		console.log('playing');
	  		break;
		case YT.PlayerState.PAUSED:
			clearInterval(keepAlive)
	  		console.log('paused');
	  		break;
		case YT.PlayerState.BUFFERING:
	  		console.log('buffering');
	  		break;
		case YT.PlayerState.CUED:
	  		console.log('video cued');
	  	break;
  	}
}

function keepLogged() {
	$(document).mousemove();
}