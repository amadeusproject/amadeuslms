function setAudios(files) {
  let totalTime = 0;

  files.forEach(file => {
    let audio = new Audio(file.file);

    setTimeout(function() {
      let $ballon = $('.ballon').find('p');

      $($ballon).html(file.text);

      $('.ballon').show();

      audio.play();
    }, totalTime);

    totalTime += (file.duration * 1000);
  });

  setTimeout(function() {
    $('.ballon').hide();
  }, totalTime);
}