class Avatar {
  constructor({ trigger = $("#avatar"), cloudTrigger = $("#cloudyInfo"), introAudios = [], cloudAudios = [] } = {}) {
    this.$trigger = trigger;
    this.$cloudTrigger = cloudTrigger;

    this.intro = introAudios;
    this.cloud = cloudAudios;
    this.playing = false;
  }

  Init() {
    $(".avatarBox").show();
    this.playIntro();

    this.$trigger.parent().hide();

    if (this.cloud.length > 0) {
      this.$cloudTrigger
        .removeAttr("data-toggle")
        .removeAttr("data-original-title")
        .css("cursor", "pointer");

      let avatar = this;

      this.$cloudTrigger.on("click", function() {
        avatar.playCloud();
      });
    }
  }

  playIntro() {
    this.setAudios(this.intro);
  }

  playCloud() {
    if (!this.playing) {
      $("#tagCloudy").css("box-shadow", "0 0 0 999px rgba(0, 0, 0, 0.5)");
      $(".avatarBox").css("z-index", "9999");
      $("#otherIndicators svg").css("filter", "brightness(0.5)");
      $(".graph-container svg").css("filter", "brightness(0.5)");

      let totalTime = this.setAudios(this.cloud);

      setTimeout(function() {
        $("#tagCloudy").css("box-shadow", "none");
        $("#otherIndicators svg").css("filter", "brightness(1)");
        $(".graph-container svg").css("filter", "brightness(1)");
      }, totalTime);
    }
  }

  setAudios(files) {
    let avatar = this;
    avatar.playing = true;

    let totalTime = 0;

    files.forEach(file => {
      let audio = new Audio(file.file);

      if (file.resource_link !== null && file.resource_link !== undefined) {
        this.showResourcesTable(file.resource_link, file.tagName);
      }

      setTimeout(function() {
        let $ballon = $(".ballon").find("p");

        $($ballon).html(file.text);

        $(".ballon").show();

        // audio.play();
      }, totalTime);

      totalTime += file.duration * 1000;
    });

    setTimeout(function() {
      $(".ballon").hide();
      avatar.playing = false;
    }, totalTime);

    return totalTime;
  }

  showResourcesTable(link, tagName) {
    d3.select("#modal_cloudy_loading_ball").style("display", "inherit");
    d3.select("#modal-table").style("display", "none");

    const modal = document.querySelector("#tagModal");
    const container = d3.select("#resources-list");

    modal.querySelector("#modalTittle").innerText = `Tag: ${tagName.toUpperCase()}`;

    container.selectAll(".resource").remove();

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

        return p1 > p2 ? 1 : p1 < p2 ? -1 : d1.qtd_access < d2.qtd_access ? 1 : d1.qtd_access > d2.qtd_access ? -1 : 0;
      });

      makeTable(dataset, "#table-container", "#resources_pag", 10);

      d3.select("#modal_cloudy_loading_ball").style("display", "none");
      d3.select("#modal-table").style("display", "inherit");
    });

    $("#tagModal").modal("show");
  }
}
