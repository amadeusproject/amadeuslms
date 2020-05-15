class Avatar {
  constructor({
    trigger = $('#avatar'),
    cloudTrigger = $('#cloudyInfo'),
    indTrigger = $('#indicatorsInfo'),
    ganntTrigger = $('#ganntInfo'),
    introAudios = [],
    ganntAudios = [],
    ganntTipAudios = [],
  } = {}) {
    this.$trigger = trigger;
    this.$ganntTrigger = ganntTrigger;
    this.$cloudTrigger = cloudTrigger;
    this.$indTrigger = indTrigger;

    this.intro = introAudios;
    this.cloud = [];
    this.indicators = [];
    this.gannt = ganntAudios;

    this.cloudTips = null;
    this.indTips = null;
    this.ganntTips = ganntTipAudios;

    this.playing = false;
    this.textTimeout = null;
    this.audio = null;
    this.counter = 0;
    this.duration = 0;
    this.hasAudio = false;

    this.$playBtn = $('.controls #play');
    this.$stopBtn = $('.controls #stop');
    this.$pauseBtn = $('.controls #pause');
    this.$replayBtn = $('.controls #replay');
    this.$previousBtn = $('.controls #previous');
    this.$nextBtn = $('.controls #next');
    this.$audioBtn = $('.controls #audio');
    this.$noAudioBtn = $('.controls #audioOff');

    this.playable = {

    };
    this.lastPlayed = '';
  }

  Init() {
    this.$replayBtn.hide();
    this.$previousBtn.hide();
    this.$noAudioBtn.hide();
    this.$stopBtn.hide();

    this.playIntro();

    if (this.gannt.length > 0) {
      this.$ganntTrigger.removeAttr('data-toggle')
          .removeAttr('data-original-title')
          .css('cursor', 'pointer');

      let avatar = this;

      this.$ganntTrigger.on('click', function() {
        avatar.playGannt();
      });
    }

    if (this.ganntTips.length > 0) {
      $('#ganntTips').on('click', function() {
        avatar.playGannt(true);
      });

      $('#ganntTips').css('cursor', 'pointer').show();
    }

    this.InitBtns();
  }

  InitBtns() {
    let avatar = this;

    avatar.$playBtn.on('click', function() {
      avatar.resume();
    });

    avatar.$stopBtn.on('click', function() {
      avatar.stop();
    });

    avatar.$pauseBtn.on('click', function() {
      avatar.pause();
    });

    avatar.$replayBtn.on('click', function() {
      avatar.replay();
    });

    avatar.$previousBtn.on('click', function() {
      avatar.handlePrevious();
    });

    avatar.$nextBtn.on('click', function() {
      avatar.handleNext();
    });

    avatar.$audioBtn.on('click', function() {
      avatar.setAudio();
    });

    avatar.$noAudioBtn.on('click', function() {
      avatar.unsetAudio();
    });

    $('#avatar_mask').on('click', function() {
      avatar.stop();
    });
  }

  setCloudAudios(info, tips) {
    let avatar = this;

    avatar.cloudTips = tips;

    if (avatar.cloudTips.length > 0) {
      $('#cloudyTips').on('click', function() {
        avatar.playCloud(true);
      });

      $('#cloudyTips').css('cursor', 'pointer').show();
    }

    avatar.cloud = info;

    if (avatar.cloud.length > 0) {
      avatar.$cloudTrigger.removeAttr('data-toggle')
          .removeAttr('data-original-title')
          .css('cursor', 'pointer');

      avatar.$cloudTrigger.on('click', function() {
        avatar.playCloud();
      });
    }
  }

  setIndicatorsAudios(info, tips) {
    let avatar = this;

    avatar.indTips = tips;

    if (avatar.indTips.length > 0) {
      $('#indicatorsTips').on('click', function() {
        avatar.playIndicators(true);
      });

      $('#indicatorsTips').css('cursor', 'pointer').show();
    }

    avatar.indicators = info;

    if (avatar.indicators.length > 0) {
      avatar.$indTrigger.removeAttr('data-toggle')
          .removeAttr('data-original-title')
          .css('cursor', 'pointer');

      avatar.$indTrigger.on('click', function() {
        avatar.playIndicators();
      });
    }
  }

  play(files) {
    let avatar = this;

    if (!avatar.playing) {
      avatar.$playBtn.hide();
      avatar.$replayBtn.hide();
      avatar.$previousBtn.hide();
      avatar.$pauseBtn.show();
      avatar.$stopBtn.show();
      avatar.$nextBtn.show();

      avatar.activePlayslist = files;
      avatar.counter = 0;

      if (avatar.hasAudio) {
        avatar.audio.src = files[avatar.counter].file;
      }

      avatar.showText(files[avatar.counter]);

      avatar.playing = true;
    }
  }

  stop() {
    let avatar = this;

    window.clearInterval(avatar.textTimeout);

    $('.ballon').hide();
    $('.mouth').removeClass('mouthSpeak');

    let $ballon = $('.ballon').find('p');

    avatar.removeTagEffect($ballon);

    avatar.duration = 0;
    avatar.counter = 0;
    avatar.playing = false;

    if (avatar.hasAudio) {
      avatar.audio.pause();
    }

    avatar.$replayBtn.show();
    avatar.$stopBtn.hide();
    avatar.$pauseBtn.hide();
    avatar.$playBtn.hide();

    avatar.clearMask();
  }

  pause() {
    let avatar = this;

    window.clearInterval(avatar.textTimeout);
    $('.mouth').removeClass('mouthSpeak');

    if (avatar.hasAudio) {
      avatar.audio.pause();
    }

    avatar.$playBtn.show();
    avatar.$pauseBtn.hide();
  }

  resume() {
    this.showText(this.activePlayslist[this.counter]);

    this.$playBtn.hide();
    this.$pauseBtn.show();
  }

  replay() {
    switch (this.lastPlayed) {
      case 'intro':
        this.playIntro();
        break;
      case 'cloud':
        this.playCloud();
        break;
      case 'cloudTips':
        this.playCloud(true);
        break;
      case 'indicators':
        this.playIndicators();
        break;
      case 'indTips':
        this.playIndicators(true);
        break;
      case 'gannt':
        this.playGannt();
        break;
      case 'ganntTips':
        this.playGannt(true);
        break;
    }

    this.$replayBtn.hide();
    this.$stopBtn.show();
    this.$pauseBtn.show();
  }

  showText(file) {
    let avatar = this;
    avatar.duration = 0;

    let $ballon = $('.ballon').find('p');

    avatar.removeTagEffect($ballon);

    $($ballon).html(file.text);

    if (file.resource_link !== null && file.resource_link !== undefined) {
      avatar.showResourcesTable(file.resource_link, file.tagName);
    }

    avatar.addTagEffect($ballon);

    $('.ballon').show();
    $('.mouth').addClass('mouthSpeak');

    if (avatar.hasAudio) {
      avatar.audio.play();
    }

    avatar.textTimeout = setInterval(function() {
      if (avatar.duration >= file.duration) {
        avatar.handleNext();
      }

      avatar.duration += 1;
    }, 1000);
  }

  setAudio() {
    let avatar = this;

    let index =
        avatar.counter < avatar.activePlayslist.length ? avatar.counter : 0;

    avatar.audio = new Audio(avatar.activePlayslist[index].file);

    avatar.hasAudio = true;

    avatar.$audioBtn.hide();
    avatar.$noAudioBtn.show();

    if (avatar.playing) {
      window.clearInterval(avatar.textTimeout);
      avatar.showText(avatar.activePlayslist[avatar.counter])
    }
  }

  unsetAudio() {
    let avatar = this;

    avatar.audio.pause();
    avatar.audio = null;

    avatar.hasAudio = false;

    avatar.$audioBtn.show();
    avatar.$noAudioBtn.hide();
  }

  handlePrevious() {
    let avatar = this;

    window.clearInterval(avatar.textTimeout);

    avatar.counter -= 1;

    $('.ballon').hide();
    $('.mouth').removeClass('mouthSpeak');

    avatar.$nextBtn.show();
    avatar.$replayBtn.hide();
    avatar.$pauseBtn.show();

    if (avatar.counter >= 0) {
      if (avatar.counter == 0) {
        avatar.$previousBtn.hide();
      }

      let file = avatar.activePlayslist[avatar.counter];

      if (avatar.hasAudio) {
        avatar.audio.src = file.file;
      }

      avatar.showText(file);
    } else {
      avatar.playing = false;

      let $ballon = $('.ballon').find('p');

      avatar.removeTagEffect($ballon);
    }
  }

  handleNext() {
    let avatar = this;

    window.clearInterval(avatar.textTimeout);

    avatar.counter += 1;

    $('.ballon').hide();
    $('.mouth').removeClass('mouthSpeak');

    avatar.$previousBtn.show();
    avatar.$replayBtn.hide();
    avatar.$pauseBtn.show();

    if (avatar.counter < avatar.activePlayslist.length) {
      if (avatar.counter == avatar.activePlayslist.length - 1) {
        avatar.$nextBtn.hide();
      }

      let file = avatar.activePlayslist[avatar.counter];

      if (avatar.hasAudio) {
        avatar.audio.src = file.file;
      }

      avatar.showText(file);
    } else {
      avatar.$nextBtn.hide();
      avatar.playing = false;
      avatar.clearMask()

      let $ballon = $('.ballon').find('p');

      avatar.removeTagEffect($ballon);

      avatar.$replayBtn.show();
      avatar.$stopBtn.hide();
      avatar.$pauseBtn.hide();
    }
  }

  playIntro() {
    this.play(this.intro);
    this.lastPlayed = 'intro';
  }

  playCloud(tips = false) {
    $('#avatar_mask').show();
    $('#tagCloudy').css('z-index', '10').css('background', '#FFFFFF');
    $('.avatarContainer').css('z-index', '9999');

    this.play(tips ? this.cloudTips : this.cloud);
    this.lastPlayed = tips ? 'cloudTips' : 'cloud';
  }

  playIndicators(tips = false) {
    $('#avatar_mask').show();
    $('#otherIndicators').css('z-index', '10').css('background', '#FFFFFF');
    $('.avatarContainer').css('z-index', '9999');

    this.play(tips ? this.indTips : this.indicators);
    this.lastPlayed = tips ? 'indTips' : 'indicators';
  }

  playGannt(tips = false) {
    $('#avatar_mask').show();
    $('#gantt').css('z-index', '10').css('background', '#FFFFFF');
    $('.avatarContainer').css('z-index', '9999');

    this.play(tips ? this.ganntTips : this.gannt);
    this.lastPlayed = tips ? 'ganntTips' : 'gannt';
  }

  clearMask() {
    $('#avatar_mask').hide();
    $('#tagCloudy').css('background', 'transparent').css('z-index', '1');
    $('#otherIndicators').css('background', 'transparent').css('z-index', '1');
    $('#gantt').css('background', 'transparent').css('z-index', '1');
  }

  addTagEffect($ballon) {
    let tags = $('#cloudy').find('svg').find('.vis').find('text');
    $($ballon).find('.shineTag').each(function(index, item) {
      tags.each(function(i, tag) {
        if ($(tag).text() == $(item).text()) {
          $(tag).addClass('shiningTag');
        }
      })
    });
  }

  removeTagEffect($ballon) {
    let tags = $('#cloudy').find('svg').find('.vis').find('text');
    $($ballon).find('.shineTag').each(function(index, item) {
      tags.each(function(i, tag) {
        if ($(tag).text() == $(item).text()) {
          $(tag).removeClass('shiningTag');
        }
      })
    });
  }

  showResourcesTable(link, tagName) {
    d3.select('#modal_cloudy_loading_ball').style('display', 'inherit');
    d3.select('#modal-table').style('display', 'none');

    const modal = document.querySelector('#tagModal');
    const container = d3.select('#resources-list');

    modal.querySelector('#modalTittle').innerText =
        `Tag: ${tagName.toUpperCase()}`;

    container.selectAll('.resource').remove();

    $.get(link, dataset => {
      dataset = dataset.sort((d1, d2) => {
        if (isNaN(d1.qtd_access) || +d1.qtd_access == 0) {
          d1.qtd_access = 0;
        }

        if (isNaN(d2.qtd_access) || +d2.qtd_access == 0) {
          d2.qtd_access = 0;
        }

        if (isNaN(d1.qtd_my_access) || +d1.qtd_my_access == 0) {
          d1.qtd_my_access = 0;
        }

        if (isNaN(d2.qtd_my_access) || +d2.qtd_my_access == 0) {
          d2.qtd_my_access = 0;
        }

        const p1 = d1.qtd_my_access / d1.qtd_access,
              p2 = d2.qtd_my_access / d2.qtd_access;

        return p1 > p2 ? 1 :
                         p1 < p2 ? -1 :
                                   d1.qtd_access < d2.qtd_access ?
                                   1 :
                                   d1.qtd_access > d2.qtd_access ? -1 : 0;
      });

      makeTable(dataset, '#table-container', '#resources_pag', 10);

      d3.select('#modal_cloudy_loading_ball').style('display', 'none');
      d3.select('#modal-table').style('display', 'inherit');
    });

    $('#tagModal').modal('show');
  }
}
