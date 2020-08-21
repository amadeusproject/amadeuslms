/**
 * WARNING Formato de data precisa ser atualizado com a adição de um idioma
 * "Date.prototype.toStringFormat"
 */
/**
    var chartConfig = {
        name: "tasksGantt",
        target: "#gantt",
        data: {% autoescape off %} {{ graph_data }} {% endautoescape %},//[{
   date: { start: "", end: "", delay: "" }, percent: 0.0, action: "", name: "",
   done: false }], metadata: { maxrow: 5, date: { start: init_date, end:
   end_date },// (([0-9]{1,2})[ ]+de[ ]+([^0-9 ]+)[ ]+de+[
   ]+([0-9]{2,4}))|(([^0-9 \)\n\t]+)[ ]+([0-9]{1,2}),[ ]+([0-9]{2,4}))
            min_period: "",
            now: "",
        },
        status: ["late", "on_time", "planned", "lost", "complete_late",
   "completed"], tooltip: { text: "",
        },
        interactions: {
            button: {

            },
            filter: {

            }
        }
    }
    var ganttChart = new Gantt(chartConfig)._draw();
*/
/*
var chartConfig = {
    name: "tasksGantt",
    target: "#gantt",
    data: data,//[{ date: { start: "", end: "", delay: "" }, percent: 0.0,
action: "", name: "", done: false }], dimensions: { width: 0, height: 250 },
    metadata: {
        maxrow: 5,
        date: { start: "", end: "" },// (([0-9]{1,2})[ ]+de[ ]+([^0-9 ]+)[
]+de+[ ]+([0-9]{2,4}))|(([^0-9 \)\n\t]+)[ ]+([0-9]{1,2}),[ ]+([0-9]{2,4}))
        min_period: "",
        now: "",
    },
    texts: {
        status: ["late", "on_time", "planned", "lost", "complete_late",
"completed"],
    },
    tooltip: {
        text: "",
    },
    interactions: {
        button: {

        },
        filter: {

        }
    }
}
*/
class Gantt {
  constructor(chartConfig) {
    var a = this;
    this.chartConfig = chartConfig;
    this.name = chartConfig.name || ('gant' + Gantt.ngants++);
    this.svg = d3.select(chartConfig.target)
                   .append('svg')
                   .attr('id', this.name)
                   .attr('class', 'gantt-svg');

    this.svg.append('defs');  // Definições de padrões de textura
    var focus =
        this.svg.append('g').attr('class', 'focus');  // Grupo com atividades
    var context =
        this.svg.append('g').attr('class', 'context');  // Linha do tempo


    // Definindo os Paterns em Defs
    (function patterns() {
      a.svg.select('defs')
          .selectAll('pattern')
          .data(chartConfig.status)
          .enter()
          .append('pattern')
          .attr(
              'id',
              function(d, i) {
                return 'hachura-status-' + (i + 1)
              })
          .attr('patternUnits', 'userSpaceOnUse')
          .attr('width', '5px')
          .attr('height', '5px')
          .append('path')
          .attr('d', 'M 0 5 L 5 0')
          .attr(
              'class',
              function(d) {
                return d
              }) /** ainda falta garantir a cor */
          .attr('stroke-width', '1px');

      var seta = a.svg.select('defs')
                     .append('pattern')
                     .attr('id', 'arrow-n')
                     .attr('width', '100px')
                     .attr('height', '100px')
                     .attr('patternUnits', 'userSpaceOnUse');
      seta.append('rect')
          .attr('width', 100)
          .attr('height', 100)
          .attr('fill', '#f1f1f1')
      seta.append('path')
          .attr('d', 'M 33,25 l 0,50 34,-25 z')
          .attr('fill', '#333');

      seta = a.svg.select('defs')
                 .append('pattern')
                 .attr('id', 'arrow-o')
                 .attr('width', '100px')
                 .attr('height', '100px')
                 .attr('patternUnits', 'userSpaceOnUse');
      seta.append('rect')
          .attr('width', 100)
          .attr('height', 100)
          .attr('fill', '#C6C6C6')
      seta.append('path')
          .attr('d', 'M 33,25 l 0,50 34,-25 z')
          .attr('fill', '#333');

      seta = a.svg.select('defs')
                 .append('pattern')
                 .attr('id', 'arrow-c')
                 .attr('width', '100px')
                 .attr('height', '100px')
                 .attr('patternUnits', 'userSpaceOnUse');
      seta.append('rect')
          .attr('width', 100)
          .attr('height', 100)
          .attr('fill', '#424242')
      seta.append('path')
          .attr('d', 'M 33,25 l 0,50 34,-25 z')
          .attr('fill', '#F1F1F1');

      seta = a.svg.select('defs')
                 .append('pattern')
                 .attr('id', 'arrow-d')
                 .attr('width', '100px')
                 .attr('height', '100px')
                 .attr('patternUnits', 'userSpaceOnUse');
      seta.append('rect')
          .attr('width', 100)
          .attr('height', 100)
          .attr('fill', '#F1F1F1')
      seta.append('path')
          .attr('d', 'M 33,25 l 0,50 34,-25 z')
          .attr('fill', '#B0B0B0');
    })();
    // Configurando dados
    this._setting_data();

    // Criando escalas
    this.x =
        d3.scaleTime()  // focus
            .domain([
              a.chartConfig.metadata.date.start, a.chartConfig.metadata.date.end
            ]);
    this.x2 = d3.scaleTime()  // context
                  .domain(this.x.domain());
    this.y =
        d3.scaleBand().domain(range(a.chartConfig.metadata.maxrow));  // focus
    this.y2 =
        d3.scaleBand().domain(range(a.chartConfig.status.length));  // context

    // Salva quais status estao filtrados
    this.filtered = range(a.chartConfig.status.length).map(function() {
      return false
    });

    this.brush = d3.brushX().on('brush end', function() {
      a._brushed(a)
    }, {
      passive: true
    });  // Função de arraste /*brushed é método da classe Gantt*/
    this.zoom = d3.zoom().scaleExtent([1, Infinity]).on('zoom', function() {
      a._zoomed(a)
    }, {passive: true});  // Função de zoom /*zoomed é método da classe Gantt*/

    focus.append('g').attr(
        'class', 'axis axis--x focus-ticks')  // Linhas de fundo
    focus.append('g').attr('class', 'axis axis--x focus-axis')  // Eixo de cima

    focus.append('rect')
        .attr('class', 'background-focus')  //Área que permite utilizar o zoom
        //.style("cursor", "move").style("fill", "none").style("pointer-events",
        //"all");


        this.focusContent = focus.append('g').attr('class', 'focusContent');
    this.contextContent = context.append('g').attr('class', 'contextContent');

    focus.append('g')
        .attr('class', 'now-line')
        .append('line')
        .attr('stroke-dasharray', '5 10');
    context.append('g')
        .attr('class', 'now-line')
        .append('line')
        .attr('stroke-dasharray', '2 5');

    d3.selectAll('.gantt-legend-status')
        .select('.status-percent')
        .text(function(
            d, i) {  // Calcula porcentagem em cima da quantidade de cada status
          return percentString(
              a.chartConfig.metadata.statuscounter[i] /
              a.chartConfig.data.length);
        });  // Imprime porcentagens sobre as legendas dos status

    context.append('g').attr('class', 'brush');

    this.ganttCard = new GanttCard(this);

    this.opened = false;
    this.percent = true;

    return this;
  }
  percent_toogle(percent) {  // Alternar visualização de percentagem da turma
    this.percent = percent || !this.percent;
    this._transform_elements(500);
    return this;
  }
  open_context() {  // Abre visualização da linha do tempo em multi pistas
    var a = this;
    clearTimeout(this.open_settimeout);
    this.open_settimeout = setTimeout(function() {
      a.close_context();
    }, 3000)

    if (this.opened) return;
    this.opened = true;
    this._draw();
    return this;
  }
  close_context() {  // Fecha a visualização da linha do tempo em uma pista
    if (!this.opened) return;

    this.opened = false;
    this._draw();

    return this;
  }
  reset(period) {  // Redimenciona zoom para periodo definido como minimo
    var a = this;

    this.gotoperiod(
        a.chartConfig.metadata.now, a.chartConfig.metadata.now, period)
    return this;
  }
  gotoperiod(
      init, end, period,
      duration) {  // Redimenciona zoom para periodo informado
    var a = this;
    if (isNaN(period)) period = 10;
    duration = duration || 500;
    var s = [
      new Date(init.getFullYear(), init.getMonth(), init.getDate() - period),
      new Date(end.getFullYear(), end.getMonth(), end.getDate() + period)
    ];
    s = s.map(function(d) {
      var temp = a.x2(d);
      return temp < 0 ? 0 : (temp > a.x2.range()[1] ? a.x2.range()[1] : temp);
    });
    a.x.domain(s.map(a.x2.invert, a.x2));

    a.solicited = true;
    a._transform_elements(duration);
    setTimeout(function() {
      a.solicited = false;
      a._transform_elements(16);
    }, duration)

    // a.svg.select(".context").select(".brush").call(a.brush.move, s);
    a.svg.select('.background-focus')
        .call(
            a.zoom.transform,
            d3.zoomIdentity.scale(a.focus_setting.width / (s[1] - s[0]))
                .translate(-s[0], 0));

    return this;
  }
  goto(data, period) {  // Redimenciona zoom para exibir atividade
    if (!data) return;
    var a = this;
    a.ganttCard.hide()
    setTimeout(function() {
      a.gotoperiod(data.date.start, data.date.end, period);
      setTimeout(function() {
        a.ganttCard.show(data);
      }, 500)
    }, 750);

    return this;
  }
  filter(status) {  // Seleciona status para ser filtrado ou desfiltrado
    var a = this;
    status = this.chartConfig.status.indexOf(status);
    this.filtered[status] = !this.filtered[status];

    this.chartConfig.interactions.filters.filter(a.filtered);

    this.notifications.transition().duration(500).attr('opacity', function(d) {
      return a.filtered[d.status] ? 1 : 0.3
    })
    a.contextRects = d3.selectAll('.contextRects').data(a.chartConfig.data)
    a.contextRects.transition().duration(500).attr('opacity', function(d) {
      return a.filtered[d.status] ? 1 : 0.2
    })

    if (this.filtered.indexOf(false) == -1 || this.filtered.indexOf(true) == -1)
    setTimeout(function() {
      a.filter_out();
    }, 500)


    return this;
  }
  filter_out() {  // Retira todos os filtros
    this.filtered = this.filtered.map(function() {
      return false
    });

    this.chartConfig.interactions.filters.filter_out();

    this.notifications.transition().duration(500).attr('opacity', 1);
    this.contextRects.transition().duration(500).attr('opacity', 1)


    return this;
  }
  _draw() {  // Desenha o gráfico
    var a = this;
    var dimensions = document.getDimensions('#' + this.name);

    var margin = {
      top: 15,
      bottom: 5,
      left: 15,
      right: 15,
    }

                 this.focus_setting = {
      top: margin.top,
      left: margin.left,
      width: dimensions.w - margin.left - margin.right,
      height: 200,
    };
    this.context_setting = {
      top: a.focus_setting.top + a.focus_setting.height + margin.bottom,
      left: margin.left,
      width: a.focus_setting.width,
      height: 15,
      height2: 15,
      size_bar: 13,
      size_bar2: 4,
    };
    this.x.range([0, this.focus_setting.width]),
        this.y.rangeRound([0, this.focus_setting.height]).padding(0.4);
    this.x2.range([0, this.context_setting.width]);
    // Essa altura é definida considerando as sobreposições iguais ao abrir a
    // barra da linha do tempo
    var n_status = this.chartConfig.metadata.statuscounter.length;
    var h_axis =
        (this.context_setting.size_bar - this.context_setting.size_bar2) *
        n_status / (n_status - 1);
    this.y2.rangeRound([0, h_axis]);

    var focus = a.svg.select('.focus').attr(
        'transform',
        'translate(' + this.focus_setting.left + ',' + this.focus_setting.top +
            ')')
    focus.select('.background-focus')
        .attr('width', this.focus_setting.width)
        .attr('height', this.focus_setting.height);

    var context =
        a.svg.select('.context')
            .attr(
                'transform',
                'translate(' + this.context_setting.left + ',' +
                    (this.context_setting.top + this.context_setting.height2) +
                    ')' +
                    'scale(1,-1)');  // Escala vertical invertida para facilitar
                                     // o efeito de abrir context

    this.svg
        .selectAll('.now-line')  // Altura das duas linhas de agora
        .select('line')
        .attr('x1', 0)
        .attr('y1', 0)
        .attr('x2', 0)
        .attr('y2', function(d, i) {
          return i == 0 ? a['focus_setting'].height :
                          a['context_setting'][a.opened ? 'height2' : 'height']
        });

    function transformRect(data, i) {
      return 'translate(' + (a.x(data.date.start)) + ',' + a.y(data.position) +
          ')';
    }

    a.focusContent.selectAll('.notifications')
        .data(a.chartConfig.data)
        .enter()
        .append('g')
        .attr(
            'class',
            function(d) {
              return 'notifications '
            })  // status-" + d.status })
        .attr(
            'id',
            function(d, i) {
              return 'notification-' + i
            })
        .attr('transform', transformRect);

    var rects = [
      {class: 'notification back-bar status-', scale: false},
      {class: 'notification pro-bar status-', scale: true}
    ];
    this.notifications = a.focusContent.selectAll('.notifications');
    this.notifications.selectAll('rect')
        .data(function(d) {
          return [d, d];
        })
        .enter()
        .append('rect')
        .attr(
            'class',
            function(d, i) {
              return rects[i].class + d.status
            })
        .attr('width', 0)
        .attr('height', a.y.bandwidth())
        .style(
            'fill',
            function(d, i) {
              if (i == 0)
                return 'url(#hachura-status-' + (d.status + 1) + ')none'
            })
        .style('stroke-width', 0);
    this.notifications.selectAll('text')
        .data(function(d) {
          return [d];
        })
        .enter()
        .append('text')
        .attr('class', 'notification-text')
        .attr('x', '5px')
        .attr('y', a.y.bandwidth() / 2)
        .attr('dy', '0.4em')
        //.text(function(d){return d.action +" "+ d.name})



        this.notifications.on('click', function(d) {
          a.ganttCard.show(d)
        });

    this.contextContent.selectAll('.backContextBar')
        .data([{}])
        .enter()
        .append('rect')
        .attr('class', 'backContextBar');
    this.contextContent.selectAll('.backContextBar')
        .data([{}])
        .attr('width', this.context_setting.width)
        .attr('height', this.context_setting.size_bar)
        .attr('fill', '#ddd');
    this.contextContent.selectAll('.arrow-scroll')
        .data([-1, 1])
        .enter()
        .append('g')
        .attr(
            'class',
            function(d, i) {
              return 'arrow-scroll way-' + (d == -1 ? 'l' : 'r')
            })
        .append('rect')

            this.contextContent.selectAll('.arrow-scroll')
        .data([-1, 1])
        .attr(
            'transform',
            function(d, i) {
              return 'translate(' + (i ? a.context_setting.width : 0) + ',0)' +
                  'scale(' + d * a.context_setting.size_bar / 100 + ',' +
                  a.context_setting.size_bar / 100 + ')';
            })
        .select('rect')
        .attr('width', 100)
        .attr('height', 100)
        .style('fill', 'url(#arrow-n)none')
        .on('mouseover',
            function(d, i) {
              if (d3.select(this).style('fill') == 'url("#arrow-d") none')
                return;
              d3.select(this).style('fill', 'url(#arrow-o)none');
            })
        .on('mouseout',
            function(d, i) {
              if (d3.select(this).style('fill') == 'url("#arrow-d") none')
                return;
              d3.select(this).style('fill', 'url(#arrow-n)none');
              a._clear_next();
            })
        .on('mousedown',
            function(d, i) {
              if (d3.select(this).style('fill') == 'url("#arrow-d") none')
                return;
              d3.select(this).style('fill', 'url(#arrow-c)none');

              a._next(d * 0.2, 200);
              a.scrool_mouse_down = setTimeout(function() {
                a.scrool_mouse_down2 = setInterval(function() {
                  a._next(d * 0.2, 100);
                }, 120)
              }, 500);
            })
        .on('mouseup',
            function(d, i) {
              if (d3.select(this).style('fill') == 'url("#arrow-d") none')
                return;
              d3.select(this).style('fill', 'url(#arrow-o)none');
              a._clear_next();
            })


            this.contextContent
        .attr(
            'transform',
            'translate(0,' +
                (this.context_setting.height - this.context_setting.size_bar) /
                    2 +
                ')')
        .selectAll('.contextRects')
        .data(a.chartConfig.data)
        .enter()
        .append('rect')
        .attr(
            'class',
            function(d) {
              return 'contextRects status-' + d.status;
            })
        .attr('y', 0)
        .attr(
            'x',
            function(d) {
              return a.x2(d.date.start)
            })
        .attr('width', 0)
        .attr('height', this.context_setting.size_bar);
    this.contextRects = this.contextContent.selectAll('.contextRects')
                            .data(a.chartConfig.data)
                            .transition()
                            .duration(500)
                            .attr(
                                'y',
                                function(d) {
                                  return a.opened ? a.y2(d.status) : 0
                                })
                            .attr(
                                'rx',
                                (a.opened ? this.context_setting.size_bar2 :
                                            this.context_setting.size_bar) /
                                    2)
                            .attr(
                                'ry',
                                (a.opened ? this.context_setting.size_bar2 :
                                            this.context_setting.size_bar) /
                                    2)
                            .style('stroke', '#ddd')
                            .style('stroke-width', '.5')
                            .attr(
                                'height',
                                a.opened ? this.context_setting.size_bar2 :
                                           this.context_setting.size_bar)
                            .attr(
                                'x',
                                function(d) {
                                  return a.x2(d.date.start)
                                })
                            .attr('width', function(d) {
                              return a.x2(d.date.end) - a.x2(d.date.start)
                            });

    this.xAxis =
        d3.axisBottom(this.x).ticks(Math.floor(a.focus_setting.width / 110));
    this.xTicks = d3.axisBottom(this.x)
                      .ticks(Math.floor(a.focus_setting.width / 110))
                      .tickSize(a.focus_setting.height + margin.top / 2);

    focus.select('.focus-axis')
        .attr('transform', 'translate(0,' + (-margin.top / 2) + ')')
    focus.select('.focus-ticks')
        .attr('opacity', 0.3)
        .attr('transform', 'translate(0,' + (-margin.top / 2) + ')');

    this.zoom
        .translateExtent(
            [[0, 0], [a.focus_setting.width, a.focus_setting.height]])
        .extent([[0, 0], [a.focus_setting.width, a.focus_setting.height]]);
    this.brush.extent([
      [0, 0],
      [
        a.context_setting.width,
        (a.opened ? a.context_setting.height2 : a.context_setting.height)
      ]
    ]);

    a.solicited = true;
    a._transform_elements(500);
    setTimeout(function() {
      a.solicited = false;
      a._transform_elements(16);
    }, 500)

    context.select('.brush').selectAll('rect').remove();
    context.select('.brush').call(a.brush).call(
        a.brush.move, [a.x2(a.x.domain()[0]), a.x2(a.x.domain()[1])]);
    focus.select('.background-focus').call(a.zoom);

    context.select('.selection').attr('fill', '#444').attr('fill-opacity', 0.6);


    return this;
  }
  _next(percent, duration) {
    var a = this;
    var range = a.x.domain();
    range = range.map(function(d) {
      return d.getTime()
    })
    var period = (range[1] - range[0]) * percent;
    a.gotoperiod(
        new Date(range[0] + period), new Date(range[1] + period), 0, duration);
    return this;
  }
  _clear_next() {
    clearTimeout(this.scrool_mouse_down);
    clearInterval(this.scrool_mouse_down2);
    return this;
  }
  _zoomed(a) {  // Ação de Zoom
    if (d3.event.sourceEvent && d3.event.sourceEvent.type === 'brush')
      return;  // ignore zoom-by-brush
    var t = d3.event.transform;
    a.x.domain(t.rescaleX(a.x2).domain());

    if (!a.solicited) {
      this._transform_elements(16);
    }

    a.svg.select('.context')
        .select('.brush')
        .call(a.brush.move, a.x.range().map(t.invertX, t));
    return this;
  }
  _brushed(a) {  // Ação de Arraste
    if (d3.event.sourceEvent && d3.event.sourceEvent.type === 'zoom')
      return;  // ignore brush-by-zoom
    var s = d3.event.selection || a.x2.range();
    a.x.domain(s.map(a.x2.invert, a.x2));

    if (!a.solicited) {
      this._transform_elements(16);
    }
    a.svg.select('.background-focus')
        .call(
            a.zoom.transform,
            d3.zoomIdentity.scale(a.focus_setting.width / (s[1] - s[0]))
                .translate(-s[0], 0));
  }
  _transform_elements(
      transition) {  // Atualiza elementos da tela na linha do tempo
    var a = this;
    transition = isNaN(transition) ? 0 : transition;

    a.svg.select('.focus')
        .select('.focus-axis')
        .transition()
        .duration(transition)
        .call(a.xAxis)
        .selectAll('text')
        .style('background', '#FFFFFF');

    a.svg.select('.focus')
        .select('.focus-ticks')
        .transition()
        .duration(transition)
        .call(a.xTicks);
    var rects = [
      {class: 'notification back-bar status-', scale: false},
      {class: 'notification pro-bar status-', scale: true}
    ];

    function widthRect(data, i) {
      return (
          (a.x(data.date.end) - a.x(data.date.start)) *
          (rects[i].scale && a.percent ? data.percent : 1));
    }
    function transformRect(data, i) {
      return 'translate(' + (a.x(data.date.start)) + ',' + a.y(data.position) +
          ')';
    }

    a.notifications.transition()
        .duration(transition)
        .attr('transform', transformRect)
    a.notifications.selectAll('rect')
        .data(function(d) {
          return [d, d]
        })
        .transition()
        .duration(transition)
        .attr('width', widthRect);
    abrev_init();
    a.notifications.select('text')
        .transition()
        .delay(transition)
        .duration(transition / 10)
        .text(function(d, i) {
          return abreviate(
              `${d.action} ${d.name}`,
              Math.max(widthRect(d, 0), widthRect(d, 1)), 15)
        })
        .style('font-weight', 'bold');
    abrev_end();
    this.svg.selectAll('.now-line')
        .transition()
        .duration(transition)
        .attr('transform', function(d, i) {
          return 'translate(' +
              a[i == 0 ? 'x' : 'x2'](a.chartConfig.metadata.now) + ',0)'
        })

    a.svg.select('.context')
        .select('.selection')
        .attr('fill', '#444')
        .attr('fill-opacity', 0.6);

    // Scroll extremes borders
    if (a.x2(a.x.domain()[0]) == a.x2.range()[0]) {
      d3.select('.way-l').select('rect').style('fill', 'url(#arrow-d)none')
      a._clear_next()
    } else if (
        d3.select('.way-l').select('rect').style('fill') ==
        'url("#arrow-d") none')
      d3.select('.way-l').select('rect').style('fill', 'url(#arrow-n)none')

      if (a.x2(a.x.domain()[1]) == a.x2.range()[1]) {
        d3.select('.way-r').select('rect').style('fill', 'url(#arrow-d)none')
        a._clear_next()
      }
    else if (
        d3.select('.way-r').select('rect').style('fill') ==
        'url("#arrow-d") none')
      d3.select('.way-r').select('rect').style('fill', 'url(#arrow-n)none')

    //       a.open_context();
  }
  _setting_data() {  // Setting Data
    chartConfig = this.chartConfig;

    chartConfig.metadata.now =
        new Date(chartConfig.metadata.now);  // Transforma string em objeto Date
    if (chartConfig.metadata.now.toString() == 'Invalid Date')
      chartConfig.metadata.now = new Date();
    var now = chartConfig.metadata.now.getTime();  // salva numero para comparar

    // auxiliares para os tratamentos type2
    var statuscounter = this.chartConfig.metadata.statuscounter =
        [0, 0, 0, 0, 0, 0];
    var positions =
        [];  // Auxilio no calculo das pistas para evitar sobreposição
    for (var i = 0; i < chartConfig.metadata.maxrow; i++) positions.push(null);

    function type(d, i) {  // Validação linha a linha

      if (d == undefined) {
        return;
      }
      if (d.date == undefined || d.date.start == undefined ||
          d.date.start == '' || d.date.end == undefined || d.date.end == '' ||
          d.name == undefined) {
        console.error('invalid row of dataSet "' + i + '" ');
        throw new Exception();
      }

      // Configurando percent
      d.percent = d.percent || 0;  // undefined para 0
      d.percent = +d.percent;      // string para number
      if (d.percent > 1) d.percent = 1;
      if (d.percent < 0) d.percent = 0;

      // Configurando datas
      d.date.start = new Date(d.date.start);
      d.date.end = new Date(d.date.end);

      if ((d.date.start.toString() ==
           'Invalid Date') ||  // Data de inicio inválida
          (d.date.end.toString() == 'Invalid Date') ||  // Data de fim inválida
          d.date.start.getTime() >
              d.date.end.getTime())  // inicio depois do fim
      {
        console.error('invalid dates in row of dataSet "' + i + '" ');
        throw new Exception();
      }
      return d;
    }

    function type2(d, i) {  // Settando status e posições e Delay
      // Delay
      if (d.date.delay === undefined || d.date.delay == '') {
        d.date.delay = null;
      } else {
        if (d.date.delay == 'infinity')
          d.date.delay = null;
        else
          d.date.delay = new Date(d.date.delay);
      }
      if (d.date.delay !== null &&
          d.date.end.getTime() >
              d.date.delay.getTime())  // fim depois do atraso
      {
        console.error(
            'invalid delay date in row of dataSet "' + i + '" name:"' + d.name +
            '"');
        d.date.delay = new Date(d.date.end);
      }


      // Status
      var start = d.date.start.getTime(), end = d.date.end.getTime(),
          delay = d.date.delay !== null ? d.date.delay.getTime() : null;

      if (d.done == true) {
        if (d.doneLate) {
          d.status = 4;
          statuscounter[4]++;
        } else {
          d.status = 5;
          statuscounter[5]++;
        }
      } else if (now < start) {
        d.status = 2;
        statuscounter[2]++;
      } else if (now <= end && now >= start) {
        d.status = 1;
        statuscounter[1]++;
      } else if (delay !== null && now >= delay) {
        d.status = 3;
        statuscounter[3]++;
      } else {
        d.status = 0;
        statuscounter[0]++;
      }

      // Settando Posição - Evitando sobreposição - Deve estar ordenado por data
      var pos = positions.indexOf(null);
      if (pos == -1) {
        positions = positions.map(function(d) {
          if (d != null && start > d.date.end.getTime()) return null;
          return d;
        });
        var pos = positions.indexOf(null);
        if (pos == -1) {
          chartConfig.metadata.maxrow++;
          pos = positions.push(null) -
              1;  // Captura ultimo indice do vetor após a inserção.
        }
      }
      d.position = pos;
      positions[pos] = d;

      return d;
    }

    function sortByDate(d1, d2) {
      var start1 = d1.date.start.getTime(), start2 = d2.date.start.getTime();
      return start1 > start2 ? 1 : (start1 < start2 ? -1 : 0);
    }

    function sortbyStatus(d1, d2) {
      return d1.status > d2.status ?
          -1 :
          (d1.status < d2.status ? 1 : sortByDate(d1, d2));
    }

    chartConfig.data = chartConfig.data.map(type);

    chartConfig.data.sort(sortByDate);

    // garantindo os extremos da linha do tempo
    chartConfig.metadata.date = chartConfig.metadata.date || {};
    chartConfig.metadata.date.start = new Date(chartConfig.metadata.date.start)
    chartConfig.metadata.date.end = new Date(chartConfig.metadata.date.end)
    if (chartConfig.metadata.date.start.toString() == 'Invalid Date') {
      chartConfig.metadata.date.start = chartConfig.data[0].date.start;
    }
    if (chartConfig.metadata.date.end.toString() == 'Invalid Date') {
      chartConfig.metadata.date.end =
          chartConfig.data[chartConfig.data.length - 1].date.end;
    }
    if (now - chartConfig.metadata.date.start.getTime() < 0)
      chartConfig.metadata.date.start = chartConfig.metadata.now;
    if (now - chartConfig.metadata.date.end.getTime() > 0)
      chartConfig.metadata.date.end = chartConfig.metadata.now;



    chartConfig.data = chartConfig.data.map(type2);

    chartConfig.data.sort(
        sortbyStatus);  // Garante a sobreposição na ordem certa

    chartConfig.data = chartConfig.data.map(function(d, i) {
      d.id = i;
      return d;
    });  // Auxilio na implementação do goto

    return this;
  }
}

Gantt.ngants = 0;

class GanttCard {
  constructor(gantt) {
    this.gantt = gantt;
    var a = this;
    d3.select('.gantt-card').select('svg').on('click', function() {
      a.hide()
    });
    d3.select('.gantt-card')
        .select('.gantt-card-close')
        .on('click', function() {
          a.hide()
        });
    this.data = gantt.chartConfig.data[0];
  }

  show(data) {
    var transition = 1000;
    data = data || {};
    var card = d3.select('.gantt-card');
    this.data = data;

    // Setting Data
    // Tittle
    card.select('.tittle').text(data.action + ' ' + data.name);

    // Start date
    card.select('.start-date')
        .select('text')
        .text(data.date.start.toStringFormat())

    // End date and Delay date
    if (data.status == 0) {
      card.select('.end-date')
          .style('display', 'inherit')
          .attr('class', 'end-date meta')
          .select('text')
          .text(data.date.end.toStringFormat());
      card.select('.delay-date').style('display', 'none');
    }
    else if (data.status == 3) {
      card.select('.delay-date')
          .style('display', 'inherit')
          .select('text')
          .text(data.date.delay.toStringFormat());
      card.select('.end-date').style('display', 'none');
    }
    else {
      card.select('.end-date')
          .style('display', 'inherit')
          .attr('class', 'end-date')
          .select('text')
          .text(data.date.end.toStringFormat());
      card.select('.delay-date').style('display', 'none');
    }

    // Percent info
    if (data.percent < 0.3) {
      card.select('.percent').style('display', 'none');
    } else {
      card.select('.percent')
          .style('display', 'inherit')
          .select('b')
          .text(percentString(data.percent));
    }

    // Alert
    if (data.status == 2 || data.status == 5) {
      card.select('.alert').style('display', 'none');
    } else {
      var temp = card.select('.alert')
                     .attr(
                         'class',
                         'alert ' + this.gantt.chartConfig.status[data.status])
                     .style('display', 'inherit');
      temp.selectAll('.text-status').style('display', 'none');
      temp.select('.text-status-' + data.status).style('display', 'inherit');
    }

    // Button
    card.select('.button-goto')
        .select('a')
        .attr('target', data.inner ? '_top' : '_blank');
    card.select('.button-goto').select('a').attr('href', data.access_link);
    card.select('.button-goto')
        .select('.other')
        .style('display', data.status <= 2 ? 'inherit' : 'none');
    card.select('.button-goto')
        .select('.lost-complete')
        .style('display', data.status <= 2 ? 'none' : 'inherit');

    // Open Card
    card.style('display', 'inherit')
        .select('.card-body')
        .style('display', 'inherit')
        .style('opacity', 0);
    var position_gantt_rect = document.querySelector('#notification-' + data.id)
                                  .querySelector('rect')
                                  .getBoundingClientRect();
    var pos_bar_card =
        document.querySelector('#bar-card').getBoundingClientRect();
    pos_bar_card.width -= 4;
    var position_gantt_rect_card =
        document.querySelector('#background-card').getBoundingClientRect();

    var rects = [
      {
        class: 'background',
        fill: '#ffffff',
        width: 1,
        height: position_gantt_rect_card.height
      },
      {
        class: 'back-bar',
        fill: 'url(#hachura-status-' + (data.status + 1) + ') none',
        width: 1,
        height: pos_bar_card.height
      },
      {
        class: 'progress-card status-' + data.status,
        width: this.gantt.percent ? data.percent : 1,
        height: pos_bar_card.height
      },
    ];
    card.selectAll('svg').selectAll('rect').data(rects).enter().append('rect');
    card.select('svg').style('background-color', 'rgba(0,0,0,0)');
    card.selectAll('svg')
        .selectAll('rect')
        .data(rects)
        .attr(
            'class',
            function(d) {
              return d.class
            })
        .style('opacity', 1)
        .attr('x', position_gantt_rect.left)
        .attr('y', position_gantt_rect.top)
        .attr('height', position_gantt_rect.height)
        .attr(
            'width',
            function(d, i) {
              return position_gantt_rect.width * d.width
            })
        .style('fill', function(d, i) {
          return d.fill
        });
    card.select('svg').transition().duration(1000).style(
        'background-color', 'rgba(0,0,0,0.5)');
    card.selectAll('svg')
        .selectAll('rect')
        .data(rects)
        .transition()
        .duration(1000)
        .attr('x', pos_bar_card.left)
        .attr('y', pos_bar_card.top)
        .attr(
            'height',
            function(d) {
              return d.height
            })
        .attr('width', function(d, i) {
          return pos_bar_card.width * d.width
        });

    card.select('#bar-card')
        .selectAll('rect')
        .data(rects)
        .transition()
        .delay(1000)
        .attr('x', 0)
        .attr('y', 0)

    card.select('svg').selectAll('rect').transition().delay(1500).style(
        'opacity', 0);


    card.select('.card-body')
        .transition()
        .delay(1000)
        .duration(500)
        .style('opacity', 1);
  }
  hide() {
    var card = d3.select('.gantt-card')
    var data = this.data;
    var position_gantt_rect = document.querySelector('#notification-' + data.id)
                                  .querySelector('rect')
                                  .getBoundingClientRect();
    card.select('svg').selectAll('rect').style('opacity', 1);
    card.select('.card-body').transition().duration(250).style('opacity', 0);
    card.transition().delay(250).select('.card-body').style('display', 'none');
    var rects = [
      1,
      1,
      this.gantt.percent ? data.percent : 1,
    ];
    card.select('svg')
        .selectAll('rect')
        .data(rects)
        .transition()
        .delay(250)
        .duration(500)
        .attr('x', position_gantt_rect.left)
        .attr('y', position_gantt_rect.top)
        .attr('height', position_gantt_rect.height)
        .attr('width', function(d) {
          return position_gantt_rect.width * d
        });
    card.select('svg').transition().delay(250).duration(500).style(
        'background-color', 'rgba(0,0,0,0)');

    card.transition().delay(750).style('display', 'none');
  }
}
function percentString(number) {
  let percent = Math.round(number * 100);

  if (isNaN(percent)) {
    percent = 0;
  }

  return '' + percent + '%';
}

Date.prototype.toStringFormat = function() {
  if (months[0] == 'January') {
    return months[this.getMonth()] + ' ' + this.getDate() + ', ' +
        this.getFullYear() + ' at ' + (this.getHours() < 9 ? '0' : '') +
        this.getHours() + ':' + (this.getMinutes() < 9 ? '0' : '') +
        this.getMinutes();
  } else {
    return '' + this.getDate() + ' de ' + months[this.getMonth()] + ' de ' +
        this.getFullYear() + ' às ' + (this.getHours() < 9 ? '0' : '') +
        this.getHours() + ':' + (this.getMinutes() < 9 ? '0' : '') +
        this.getMinutes();
  }
};
JSON.copyObject = function(object) {
  return JSON.parse(JSON.stringify(object));
};
function abrev_init() {
  d3.select('svg')
      .append('text')
      .attr('class', 'abrev-text notification-text')
      .attr('opacity', 0);
}
function abrev_end() {
  d3.select('.abrev-text').remove();
}
function abreviate_ifneed(action, name, width, font_size) {
  var abrev = d3.select('.abrev-text').style('font-size', font_size);
  var textwidth;
  function test(text) {
    abrev.text(text);
    textwidth = document.getDimensions('.abrev-text').w;
    return textwidth < (width - 10);
  }
  var text = action + ' ' + name;
  if (test(text)) return text;

  text = action.slice(0, 3) + '. ' + name;
  if (test(text)) return text;

  var n = Math.floor((width - 30) * name.length / (textwidth - 30));
  if (n > 10) {
    n = name.slice(0, n);
    text = action.slice(0, 3) + '. ' + n + '...';
    if (test(text)) return text;
  }
  n = Math.floor((width - 13) * name.length / (textwidth - 13));
  if (n > 3) {
    n = name.slice(0, n);
    text = action.slice(0, 1) + '. ' + n + '...';
    if (test(text)) return text;
  }
  n = Math.floor((width) * name.length / (textwidth));
  if (n > 3) {
    //       console.log(n);
    text = name.slice(0, n) + '...';
    if (test(text)) return text;
  }
  return '';
}

function abreviate(word, width, fontSize) {
  const wrapper = d3.select('.abrev-text').style('font-size', fontSize);
  let textWidth;

  function fit(text) {
    wrapper.text(text);
    textWidth = document.getDimensions('.abrev-text').w;

    return textWidth < (width - 10);
  }

  if (!fit(word)) {
    let length = Math.floor((width - 13) * word.length / (textWidth - 13));
    let text = `${word.slice(0, length - 3)}...`;

    if (fit(text)) {
      return text;
    }

    text = `${word.slice(0, length - 10)}...`;

    if (fit(text)) {
      return text;
    }

    text = `${word.slice(0, width - 3)}...`;

    if (fit(text)) {
      return text;
    }

    return '';
  }

  return word;
}