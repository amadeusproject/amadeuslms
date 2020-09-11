function loadLogsGraph(url, dataIni, dataEnd) {
  $.get(url, {data_ini: dataIni, data_end: dataEnd}, dataset => {
    console.log(dataset['data']);
    $('.logsgraph > .info').html('');
    //$('.logs_chart').html(dataset[ 'data' ]);
    drawChart(dataset['data']);
    $('.logsgraph .info')
        .append(`<p class='text-cloudy-legend' style="margin-right:25%"> Mínimo diário: ${
            dataset
                ['min']} </p>     <p class='text-cloudy-legend' style="margin-right:25%">Máximo diário: ${
            dataset
                ['max']}</p>            <p class='text-cloudy-legend'>Total: ${
            dataset['total']}</p>`);
  });
}


$(function() {
  const logsGraphUrl = $('.logsgraph').data('url');
  loadLogsGraph(logsGraphUrl, $('#from').val(), $('#until').val());
});

function drawChart(dataset) {
  var svg = d3.select('svg'), margin = 100,
      width = parseInt(d3.select('#logs_chart').style('width')) - margin,
      height = parseInt(d3.select('#logs_chart').style('height')) - margin;
  svg.style('width', width + margin);
  /*var yScale = d3.scale.ordinal().rangeRoundBands([height, 0], 0.1);

  var xScale = d3.scale.linear().range([0, width]);*/

  var xScale = d3.scaleBand().range([0, width]).padding(0.2),
      yScale = d3.scaleLinear().range([height, 0]);

  var g = svg.append('g').attr('transform', 'translate(' + 50 + ',' + 50 + ')');

  xScale.domain(dataset.map(function(d) {
    return d.x;
  }));
  yScale.domain([
    0,
    d3.max(
        dataset,
        function(d) {
          return d.y;
        })
  ]);

  g.append('g')
      .attr('transform', 'translate(0,' + height + ')')
      .call(d3.axisBottom(xScale))
      .append('text')
      .attr('transform', '')
      .attr('y', height - 250)
      .attr('x', width - 100)
      .attr('text-anchor', 'end')
      .attr('stroke', 'black');

  g.append('g')
      .call(d3.axisLeft(yScale)
                .tickFormat(function(d) {
                  return d;
                })
                .ticks(10))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 6)
      .attr('dy', '-5.1em')
      .attr('text-anchor', 'end')
      .attr('stroke', 'black');

  g.selectAll('.bar')
      .data(dataset)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr(
          'x',
          function(d) {
            return xScale(d.x);
          })
      .attr(
          'y',
          function(d) {
            return yScale(d.y);
          })
      .attr('width', xScale.bandwidth())
      .attr('height', function(d) {
        return height - yScale(d.y);
      });
  g.selectAll('.labels')
      .data(dataset)
      .enter()
      .append('text')
      .attr('class', 'labels')
      .text(function(d) {
        return d.y;
      })
      .attr(
          'x',
          function(d) {
            return xScale(d.x) + (xScale.bandwidth() / 2);
          })
      .attr(
          'y',
          function(d) {
            return yScale(d.y) - 5;
          })
      .attr('text-anchor', 'middle');
}