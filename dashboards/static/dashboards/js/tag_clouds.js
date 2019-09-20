let cloudWord = undefined;

function cloud() {
  const dimensions = document.getDimensions("#cloudy");
  const width =
    dimensions.w -
    $("#cloudy")
      .css("padding-left")
      .match(/[0-9]+/)[0] -
    $("#cloudy")
      .css("padding-right")
      .match(/[0-9]+/)[0];
  const height = (width * 1) / 2 > 360 ? 360 : width / 2 < 50 ? 50 : width / 2;

  $.get($("#cloudy").data("url"), data => {
    d3.select("#cloudy_loading_ball").style("display", "none");

    data = data.map(item => ({
      key: item.tag_name,
      value: item.qtd_access,
      myvalue: item.qtd_my_access,
      link: item.details_url,
      text: item.tag_name,
    }));

    data.sort((d1, d2) => (d1.value > d2.value ? -1 : d1.value < d2.value ? 1 : 0));

    const tags = data.slice(0, Math.floor((30 / 1000) * width));

    const dataconfig = {
      parent: "#cloudy",
      data: tags,
      tableData: data,
      max: 50,
      font: "Roboto,Helvetica,Arial,sans-serif",
      spiral: "rectangular",
      scale: "linear",
      angles: {
        from: 0,
        to: 0,
        n: 1,
      },
      dimensions: {
        w: width,
        h: height,
      },
      interactions: {
        click: (element, data) => {
          d3.select("#modal_cloudy_loading_ball").style("display", "inherit");
          d3.select("#modal-table").style("display", "none");

          const modal = document.querySelector("#tagModal");
          const container = d3.select("#resources-list");

          modal.querySelector("#modalTittle").innerText = `Tag: ${data.text.toUpperCase()}`;

          container.selectAll(".resource").remove();

          $.get(data.link, dataset => {
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

              return p1 > p2
                ? 1
                : p1 < p2
                ? -1
                : d1.qtd_access < d2.qtd_access
                ? 1
                : d1.qtd_access > d2.qtd_access
                ? -1
                : 0;
            });

            makeTable(
              dataset,
              ["qtd_my_access", "qtd_access", "resource_name"],
              d3.select("#table-container"),
              d3.select(".pagination"),
              10,
            );

            d3.select("#modal_cloudy_loading_ball").style("display", "none");
            d3.select("#modal-table").style("display", "inherit");
          });

          $("#tagModal").modal("show");
        },
      },
      tooltip: {
        text: "Tag: <key>\nTotal de acessos: <value> \nMeus acessos: <myvalue>",
      },
      filltext: (a, transition) => {
        transition = transition || 0;

        a.fillpattern = d3
          .scaleLinear()
          .domain([0, 1])
          .interpolate(d3.interpolateHcl)
          .range([d3.rgb("#8EC99A"), d3.rgb("#162318")]);

        const prop = a.chartConfig.mymax / a.chartConfig.max;

        a.scalePercent = (x, y) => {
          if (x > y) {
            return (y * 0.1 * prop) / x + 0.2;
          }

          return 1 - (x * 0.7) / (y * prop);
        };

        a.wordsv5
          .transition()
          .duration(transition)
          .attr("fill", (d, i) => a.fillpattern(a.scalePercent(d.myvalue, d.value)));
      },
    };

    cloudWord = new CloudWord(dataconfig);
  });
}

function view_toogle() {
  if (cloudWord) cloudWord.view_toogle();
}

$(function() {
  cloud();
});
