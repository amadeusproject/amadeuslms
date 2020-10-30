/**
 * Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 *
 * Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem,
 * ou simplesmente Amadeus LMS
 *
 * O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo
 * dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação
 * do Software Livre (FSF); na versão 2 da Licença.
 *
 * Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA
 * GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou
 * APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores
 * detalhes.
 *
 * Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título
 * "LICENSE", junto com este programa, se não, escreva para a Fundação do
 * Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301
 * USA.
 */

let calendarCount = 0;
let heatmap;
let chartConfig;
class HeatMap {
  constructor(chartConfig) {
    if (chartConfig.data === undefined || chartConfig.data.length === 0) {
      this.validData(chartConfig).empty();
    } else {
      this.validData(chartConfig).create().draw().addInteractions();
    }
  }

  validData(chartConfig) {
    const a = this;

    this.chartConfig = chartConfig;

    if (a.chartConfig.data === undefined) {
      console.error("Impossible to create heatmap without data source");
      return;
    }

    if (a.chartConfig.chart === undefined) a.chartConfig.chart = {};

    if (a.chartConfig.dataConfig === undefined) a.chartConfig.dataConfig = {};
    if (a.chartConfig.dataConfig.year === undefined)
      a.chartConfig.dataConfig.year = "year";
    if (a.chartConfig.dataConfig.month === undefined)
      a.chartConfig.dataConfig.month = "month";
    if (a.chartConfig.dataConfig.day === undefined)
      a.chartConfig.dataConfig.day = "day";
    if (a.chartConfig.dataConfig.hour === undefined)
      a.chartConfig.dataConfig.hour = "hour";
    if (a.chartConfig.dataConfig.dayOfWeek === undefined)
      a.chartConfig.dataConfig.dayOfWeek = "dayOfWeek";
    if (a.chartConfig.dataConfig.value === undefined)
      a.chartConfig.dataConfig.value = "value";

    if (
      a.chartConfig.name === undefined ||
      a.chartConfig.name === `CalendarHeatMap${calendarCount - 1}`
    ) {
      a.chartConfig.name = `CalendarHeatMap${calendarCount++}`;
    }
    if (a.chartConfig.parent === undefined) {
      a.chartConfig.parent = "body";
      a.chartConfig.svg = false;
    }
    if (a.chartConfig.svg === undefined) a.chartConfig.svg = false;

    if (a.chartConfig.dimensions === undefined) a.chartConfig.dimensions = {};
    if (a.chartConfig.dimensions.width === undefined)
      a.chartConfig.dimensions.width = 360;
    if (a.chartConfig.dimensions.height === undefined)
      a.chartConfig.dimensions.height = 600;

    if (a.chartConfig.layout === undefined) a.chartConfig.layout = {};
    if (a.chartConfig.layout.corner === undefined)
      a.chartConfig.layout.corner = 0.1;
    if (a.chartConfig.layout.padding === undefined)
      a.chartConfig.layout.padding = 0.1;
    if (a.chartConfig.layout.margin === undefined)
      a.chartConfig.layout.margin = {};
    if (a.chartConfig.layout.margin.top === undefined)
      a.chartConfig.layout.margin.top = 20;
    if (a.chartConfig.layout.margin.right === undefined)
      a.chartConfig.layout.margin.right = 20;
    if (a.chartConfig.layout.margin.bottom === undefined)
      a.chartConfig.layout.margin.bottom = 50;
    if (a.chartConfig.layout.margin.left === undefined)
      a.chartConfig.layout.margin.left = 50;
    if (a.chartConfig.layout.extrapolation === undefined)
      a.chartConfig.layout.extrapolation = 5;
    if (a.chartConfig.layout.colors === undefined)
      a.chartConfig.layout.colors = d3.interpolateGreens;
    if (a.chartConfig.layout.font_size === undefined)
      a.chartConfig.layout.font_size = 20;
    if (a.chartConfig.layout.font_size2 === undefined)
      a.chartConfig.layout.font_size2 = a.chartConfig.layout.font_size;

    a.calendar = {};
    if (!a.chartConfig.chart.calendar) {
      if (a.chartConfig.calendar === undefined) a.chartConfig.calendar = {};
      if (a.chartConfig.calendar.svg === undefined)
        a.chartConfig.calendar.svg = true;
      if (
        a.chartConfig.calendar.parent === undefined &&
        a.chartConfig.calendar.svg != true
      ) {
        a.chartConfig.calendar.parent = a.chartConfig.parent;
        a.chartConfig.calendar.svg = a.chartConfig.svg;
      }
      if (a.chartConfig.calendar.margin === undefined)
        a.chartConfig.calendar.margin = {};
      if (a.chartConfig.calendar.margin.top === undefined)
        a.chartConfig.calendar.margin.top = a.chartConfig.layout.margin.top;
      if (a.chartConfig.calendar.margin.right === undefined)
        a.chartConfig.calendar.margin.right = a.chartConfig.layout.margin.right;
      if (a.chartConfig.calendar.margin.bottom === undefined)
        a.chartConfig.calendar.margin.bottom =
          a.chartConfig.layout.margin.bottom;
      if (a.chartConfig.calendar.margin.left === undefined)
        a.chartConfig.calendar.margin.left = a.chartConfig.layout.margin.left;

      if (a.chartConfig.calendar.extrapolation === undefined)
        a.chartConfig.calendar.extrapolation =
          a.chartConfig.layout.extrapolation;
      if (a.chartConfig.calendar.extrapolation < 1)
        a.chartConfig.calendar.extrapolation = 1;
      if (a.chartConfig.calendar.axis === undefined)
        a.chartConfig.calendar.axis = {};
      if (a.chartConfig.calendar.axis.vertical === undefined)
        a.chartConfig.calendar.axis.vertical = {};
      if (a.chartConfig.calendar.axis.day === undefined)
        a.chartConfig.calendar.axis.day = {};
      if (a.chartConfig.calendar.colors === undefined)
        a.chartConfig.calendar.colors = a.chartConfig.layout.colors;
      if (a.chartConfig.calendar.texts === undefined)
        a.chartConfig.calendar.texts = {};
    } else {
      a.chartConfig.calendar = undefined;
    }

    a.hour = {};
    if (!a.chartConfig.chart.hour) {
      if (a.chartConfig.hour === undefined) a.chartConfig.hour = {};
      if (a.chartConfig.hour.svg === undefined) a.chartConfig.hour.svg = true;
      if (
        a.chartConfig.hour.parent === undefined &&
        a.chartConfig.hour.svg != true
      ) {
        a.chartConfig.hour.parent = a.chartConfig.parent;
        a.chartConfig.hour.svg = a.chartConfig.svg;
      }

      if (
        a.chartConfig.hour.model === undefined ||
        (a.chartConfig.hour.model != 12 && a.chartConfig.hour.model != 24)
      ) {
        a.chartConfig.hour.model = 4;
      }

      if (a.chartConfig.hour.margin === undefined)
        a.chartConfig.hour.margin = {};
      if (a.chartConfig.hour.margin.top === undefined)
        a.chartConfig.hour.margin.top = a.chartConfig.layout.margin.top;
      if (a.chartConfig.hour.margin.right === undefined)
        a.chartConfig.hour.margin.right = a.chartConfig.layout.margin.right;
      if (a.chartConfig.hour.margin.bottom === undefined)
        a.chartConfig.hour.margin.bottom = a.chartConfig.layout.margin.bottom;
      if (a.chartConfig.hour.margin.left === undefined)
        a.chartConfig.hour.margin.left = a.chartConfig.layout.margin.left;

      if (a.chartConfig.hour.extrapolation === undefined)
        a.chartConfig.hour.extrapolation = a.chartConfig.layout.extrapolation;

      a.chartConfig.hour.extrapolation--;

      if (a.chartConfig.hour.extrapolation < 1)
        a.chartConfig.hour.extrapolation = 1;
      if (a.chartConfig.hour.axis === undefined) a.chartConfig.hour.axis = {};
      if (a.chartConfig.hour.axis.vertical === undefined)
        a.chartConfig.hour.axis.vertical = {};
      if (a.chartConfig.hour.axis.day === undefined)
        a.chartConfig.hour.axis.day = {};
      if (a.chartConfig.hour.colors === undefined)
        a.chartConfig.hour.colors = d3.interpolateGreys;
      if (a.chartConfig.hour.texts === undefined) a.chartConfig.hour.texts = {};
    } else {
      a.chartConfig.hour = undefined;
    }

    a.chartConfig.title = d3.titleValid(a.chartConfig.title);

    if (a.chartConfig.cornerLabel !== undefined) {
      if (
        a.chartConfig.hour &&
        a.chartConfig.hour.texts.corner === undefined &&
        a.chartConfig.calendar &&
        a.chartConfig.calendar.texts.corner === undefined
      ) {
        a.chartConfig.cornerLabel = undefined;
      } else {
        if (a.chartConfig.cornerLabel.color === undefined)
          a.chartConfig.cornerLabel.color = "#fff";
        if (a.chartConfig.cornerLabel.font === undefined)
          a.chartConfig.cornerLabel.font = {};
        if (a.chartConfig.cornerLabel.font.name === undefined)
          a.chartConfig.cornerLabel.font.name = "sans-serif";
        if (a.chartConfig.cornerLabel.font.size === undefined)
          a.chartConfig.cornerLabel.font.size = 12;
        if (a.chartConfig.cornerLabel.position === undefined)
          a.chartConfig.cornerLabel.position = {};
        if (a.chartConfig.cornerLabel.position.dx === undefined)
          a.chartConfig.cornerLabel.position.dx = 0;
        if (a.chartConfig.cornerLabel.position.dy === undefined)
          a.chartConfig.cornerLabel.position.dy = 0;
      }
    }

    if (a.chartConfig.centerLabel !== undefined) {
      if (
        a.chartConfig.hour &&
        a.chartConfig.hour.texts.corner === undefined &&
        a.chartConfig.calendar &&
        a.chartConfig.calendar.texts.corner === undefined
      ) {
        a.chartConfig.centerLabel = undefined;
      } else {
        if (a.chartConfig.centerLabel.color === undefined)
          a.chartConfig.centerLabel.color = "#fff";
        if (a.chartConfig.centerLabel.font === undefined)
          a.chartConfig.centerLabel.font = {};
        if (a.chartConfig.centerLabel.font.name === undefined)
          a.chartConfig.centerLabel.font.name = "sans-serif";
        if (a.chartConfig.centerLabel.font.size === undefined)
          a.chartConfig.centerLabel.font.size = 12;
        if (a.chartConfig.centerLabel.position === undefined)
          a.chartConfig.centerLabel.position = {};
        if (a.chartConfig.centerLabel.position.dx === undefined)
          a.chartConfig.centerLabel.position.dx = 0;
        if (a.chartConfig.centerLabel.position.dy === undefined)
          a.chartConfig.centerLabel.position.dy = 0;
      }
    }

    if (a.chartConfig.tooltip !== undefined) {
      if (a.chartConfig.tooltip.text === undefined) {
        a.chartConfig.tooltip = undefined;
      } else {
        a.chartConfig.tooltip.name = `${a.chartConfig.name}-toolTip`;
        if (a.chartConfig.svg) {
          a.chartConfig.tooltip.parent = a.chartConfig.parent;
        } else {
          a.chartConfig.tooltip.parent = `#${a.chartConfig.name}-container`;
        }
      }
    }

    a.chartConfig.interactions = d3.validEvents(a.chartConfig.interactions);
    return this;
  }

  empty() {
    const a = this;

    this.svg = a.chartConfig.svg
      ? d3.select(a.chartConfig.parent)
      : d3
          .select(a.chartConfig.parent)
          .append("svg")
          .attr("id", `${a.chartConfig.name}-container`);

    this.svg.append("rect").attr("width", "100%").attr("fill", "#fff");
    this.svg
      .append("text")
      .attr("x", "20%")
      .attr("y", "50%")
      .attr("dy", "0em")
      .text("Para período selecionado não houve");
    this.svg
      .append("text")
      .attr("x", "20%")
      .attr("y", "50%")
      .attr("dy", "1em")
      .text("registro de acesso dos participantes");
  }

  create() {
    const a = this;

    this.dataSetter();

    this.svg = a.chartConfig.svg
      ? d3.select(a.chartConfig.parent)
      : d3
          .select(a.chartConfig.parent)
          .append("svg")
          .attr("id", `${a.chartConfig.name}-container`);

    if (!a.chartConfig.chart.calendar) {
      this.calendar.svg =
        a.chartConfig.calendar.svg &&
        a.chartConfig.calendar.parent === undefined
          ? this.svg
          : a.chartConfig.calendar.parent !== undefined
          ? d3.select(a.chartConfig.calendar.parent)
          : d3
              .select(a.chartConfig.calendar.parent)
              .append("svg")
              .attr("id", `${a.chartConfig.name}-calendar`);

      this.createChart(this.calendar, this.chartConfig.calendar);
    }

    if (!a.chartConfig.chart.hour) {
      this.hour.svg =
        a.chartConfig.hour.svg && a.chartConfig.hour.parent === undefined
          ? this.svg
          : a.chartConfig.hour.parent !== undefined
          ? d3.select(a.chartConfig.hour.parent)
          : d3
              .select(a.chartConfig.hour.parent)
              .append("svg")
              .attr("id", `${a.chartConfig.name}-hour`);

      this.createChart(this.hour, this.chartConfig.hour);

      this.hour.collapse = this.hour.rectsContent
        .append("g")
        .attr("id", "collapse");
      this.hour.collapse.append("path");
      this.hour.collapse.append("rect").attr("opacity", 0);
      this.hour.totalRects = this.hour.rectsContent
        .selectAll(".week")
        .data(a.hour.totalData)
        .enter()
        .append("g")
        .attr("class", "week");
      this.hour.totalRects.append("rect");

      if (a.chartConfig.centerLabel !== undefined) {
        this.hour.totalRects
          .append("text")
          .attr("class", "center")
          .attr("text-anchor", "middle");
      }

      if (a.chartConfig.cornerLabel !== undefined) {
        this.hour.totalRects
          .append("text")
          .attr("class", "corner")
          .attr("dy", "1.1em")
          .attr("dx", "0.2em");
      }
    }

    this.toolTipConstruct();

    return this;
  }

  createChart(chart, chartConfig) {
    chart.g = chart.svg.append("g");

    if (!chartConfig.axis.day.all) {
      chart.dayAxis = chart.g.append("g");
    }

    chart.scrol = chart.g.append("g");
    chart.backscrol = chart.scrol.append("rect");

    if (!chartConfig.axis.vertical.all) {
      chart.verticalAxis = chart.scrol.append("g");
    }

    chart.rectsContent = chart.scrol.append("g").attr("id", "rects");
    chart.rects = chart.rectsContent
      .selectAll(".month")
      .data(chart.data)
      .enter()
      .append("g")
      .attr("class", "month");
    chart.rects.append("rect");

    if (chartConfig.texts.center !== undefined) {
      chart.rects
        .append("text")
        .attr("class", "center")
        .attr("text-anchor", "middle");
    }

    if (chartConfig.texts.corner !== undefined) {
      chart.rects
        .append("text")
        .attr("class", "corner")
        .attr("dy", "1.1em")
        .attr("dx", "0.2em");
    }

    chart.extTriangles = chart.g.append("g");
    chart.extTriangles.append("path").attr("class", "up");
    chart.extTriangles.append("path").attr("class", "down");
  }

  draw() {
    const a = this;

    this.titleConstruct();

    this.width = a.chartConfig.dimensions.width;
    this.height = a.chartConfig.dimensions.height;
    this.calendar.margin = { top: 0, bottom: 0, left: 0, right: 0 };
    this.hour.margin = JSON.copyObject(a.calendar.margin);
    this.calendar.height = 0;
    this.hour.height = 0;

    if (!a.chartConfig.chart.calendar) {
      this.calendar.domain = a.weekDomain();
      this.calendar.margin = JSON.copyObject(a.chartConfig.calendar.margin);

      const temp = String.adjustWidth(
        "00/XXX",
        a.chartConfig.layout.font_size,
        a.width * 0.1
      );
      this.font_size = Math.min(this.chartConfig.layout.font_size, temp);
    }

    if (!a.chartConfig.chart.hour) {
      this.hour.domain = a.weekDomain(this.chartConfig.hour.model);
      this.hour.margin = JSON.copyObject(a.chartConfig.hour.margin);

      const temp = String.adjustWidth(
        a.chartConfig.hour.model === 4 ? "00h-00h" : "00XX",
        a.chartConfig.layout.font_size,
        a.width * 0.1
      );
      this.font_size = Math.min(this.chartConfig.layout.font_size, temp);
    }

    const desloc =
      a.chartConfig.title === undefined ? 0 : a.chartConfig.title.desloc;

    if (!a.chartConfig.chart.calendar) {
      this.calendar.margin.left = Math.max(
        a.calendar.margin.left,
        a.chartConfig.calendar.axis.vertical.all ? 0 : 11 + 3.0 * a.font_size
      );
      this.calendar.margin.top = Math.max(
        a.calendar.margin.top,
        (a.chartConfig.calendar.axis.day.all ? 20 : 11 + 1.05 * a.font_size) +
          desloc
      );

      this.calendar.height = a.chartConfig.calendar.extrapolation;

      if (a.calendar.domain.length < a.calendar.height) {
        a.calendar.height = a.calendar.domain.length;
      }
    }

    if (!a.chartConfig.chart.hour) {
      this.hour.margin.left = Math.max(
        a.hour.margin.left,
        a.chartConfig.hour.axis.vertical.all ? 0 : 11 + 3.0 * a.font_size
      );
      this.hour.margin.top = Math.max(
        a.hour.margin.top,
        a.chartConfig.hour.axis.day.all
          ? 20
          : 11 +
              1.05 * a.font_size +
              (a.chartConfig.chart.calendar ? desloc : 0)
      );

      this.hour.height = a.chartConfig.hour.extrapolation;

      if (a.chartConfig.hour.model < a.hour.height) {
        a.hour.height = a.chartConfig.hour.model;
      }

      this.hour.height++;
    }

    this.nVerticalRects =
      a.calendar.height +
      (a.calendar.height === 0 ? a.hour.height : a.hour.height / 1.5);

    this.size =
      a.chartConfig.dimensions.height -
      a.calendar.margin.top -
      a.calendar.margin.bottom -
      a.hour.margin.top -
      a.hour.margin.bottom;

    this.size = a.size / a.nVerticalRects;

    const tempSize =
      (a.chartConfig.dimensions.width -
        Math.max(a.calendar.margin.left, a.hour.margin.left) -
        Math.max(a.calendar.margin.right, a.hour.margin.right)) /
      7;

    this.size = Math.min(this.size, tempSize);

    a.width =
      a.size * 7 +
      Math.max(a.calendar.margin.left, a.hour.margin.left) +
      Math.max(a.calendar.margin.right, a.hour.margin.right);

    a.height =
      a.size * this.nVerticalRects +
      a.calendar.margin.top +
      a.calendar.margin.bottom +
      a.hour.margin.top +
      a.hour.margin.bottom;

    this.titleConstruct();

    if (!a.chartConfig.chart.calendar) {
      const temp = String.adjustWidth(
        "00/XXX",
        a.chartConfig.layout.font_size,
        a.calendar.margin.left * 0.8
      );
      this.font_size = Math.min(this.chartConfig.layout.font_size, temp);
    }

    if (!a.chartConfig.chart.hour) {
      const temp = String.adjustWidth(
        a.chartConfig.hour.model === 4 ? "00h-00h" : "00XX",
        a.chartConfig.layout.font_size,
        a.hour.margin.left * 0.8
      );
      this.font_size = Math.min(this.chartConfig.layout.font_size, temp);
    }

    if (!a.chartConfig.chart.hour) {
      this.calendar.size = this.size;
      this.calendar.margin.top +=
        -desloc +
        (a.chartConfig.title === undefined ? 0 : a.chartConfig.title.desloc);
      this.calendar.verticalFunction = MyDate.weekVal;
    }

    if (!a.chartConfig.chart.hour) {
      this.hour.size = this.size;

      let temp = 0;

      if (!a.chartConfig.chart.calendar) {
        this.hour.size /= 1.5;
        temp +=
          this.calendar.margin.top +
          this.calendar.margin.bottom +
          this.size * a.calendar.height;
      }

      this.hour.margin.top +=
        -(a.chartConfig.chart.calendar
          ? desloc -
            (a.chartConfig.title === undefined ? 0 : a.chartConfig.title.desloc)
          : 0) + temp;
      this.hour.verticalFunction = MyDate.dayVal;
    }

    this.day = d3
      .scaleBand()
      .rangeRound([0, 7 * a.size])
      .domain(MyDate.weekName())
      .padding(a.chartConfig.layout.padding);
    this.rCorner = (this.day.bandwidth() * a.chartConfig.layout.corner) / 2;

    if (!a.chartConfig.chart.calendar) {
      this.drawChart(a.calendar, a.chartConfig.calendar);
    }

    if (!a.chartConfig.chart.hour) {
      this.drawChart(a.hour, a.chartConfig.hour);

      const translatebefore = a.hour.g
        .attr("transform")
        .replace("translate(", "")
        .replace(")", "")
        .split(",");
      a.hour.g.attr(
        "transform",
        `translate(${translatebefore[0]}, ${
          parseFloat(translatebefore[1]) + a.size
        })`
      );

      if (!a.chartConfig.hour.axis.day.all) {
        a.hour.dayAxis.attr("transform", `translate(0, ${-a.size})`);
      }

      const max = d3.max(a.hour.totalData, (d) => d.value);
      const min = d3.min(a.hour.totalData, (d) => d.value);
      const den = max - min;

      const color = (value) => (value === 0 ? 0 : 0.1 + (value - min) / den);

      this.hour.totalRects
        .attr("fill", (d) => ((d.value - min) / den > 0.8 ? "#fff" : "#000"))
        .attr(
          "transform",
          (d, i) =>
            `translate(${a.day(MyDate.weekName()[i])}, ${
              a.hour.vertical(a.hour.vertical.domain()[0]) - a.size
            })`
        );

      this.hour.totalRects
        .select("rect")
        .attr("rx", a.rCorner)
        .attr("ry", a.rCorner)
        .attr("width", a.day.bandwidth())
        .attr("height", a.day.bandwidth())
        .attr("fill", (d) => a.chartConfig.layout.colors(color(d.value) + 0.1));

      if (a.chartConfig.hour.texts.corner !== undefined) {
        this.hour.totalRects
          .select(".corner")
          .attr("font-size", a.font_size * 0.5)
          .text((d, i) => d3.textData(d, a.chartConfig.hour.texts.center));
      }

      if (a.chartConfig.hour.texts.center !== undefined) {
        this.hour.totalRects
          .select(".center")
          .attr("font-size", a.font_size * 0.9)
          .attr("dy", a.font_size * 0.2 + a.hour.vertical.bandwidth() / 2)
          .attr("dx", a.hour.vertical.bandwidth() / 2)
          .text((d, i) =>
            String.adjustLength(
              d3.textData(d, a.chartConfig.hour.texts.center),
              a.font_size * 0.9,
              a.hour.vertical.bandwidth(),
              true
            )
          );
      }

      a.hour.hourShow = true;

      const temp = a.hour.vertical(a.hour.domain[0]);

      a.hour.collapse
        .attr("transform", `translate(${-a.size}, ${-a.size + temp / 2})`)
        .on("mouseover", function (d) {
          d3.select(this).select("path").attr("stroke-width", 2);
        })
        .on("mouseout", function (d) {
          d3.select(this).select("path").attr("stroke-width", 0);
        })
        .on("click", function (d) {
          a.hourView();
        })
        .select("rect")
        .attr("width", a.size * 8)
        .attr("height", a.size);

      this.hourView();

      d3.select("body").on("keydown", (event) => {
        if (a.calendar.on) {
          if (d3.event.keyCode == 38) {
            if (
              a.scrolMove(
                a.calendar.scrolposition - 1,
                a.calendar,
                a.chartConfig.calendar
              )
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 40) {
            if (
              a.scrolMove(
                a.calendar.scrolposition + 1,
                a.calendar,
                a.chartConfig.calendar
              )
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 34 || d3.event.keyCode == 32) {
            if (
              a.scrolMove(
                a.calendar.scrolposition + a.chartConfig.calendar.extrapolation,
                a.calendar,
                a.chartConfig.calendar
              )
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 33) {
            if (
              a.scrolMove(
                a.calendar.scrolposition - a.chartConfig.calendar.extrapolation,
                a.calendar,
                a.chartConfig.calendar
              )
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 35) {
            if (
              a.scrolMove(
                a.calendar.scrolMax,
                a.calendar,
                a.chartConfig.calendar
              )
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 36) {
            if (a.scrolMove(0, a.calendar, a.chartConfig.calendar))
              d3.event.preventDefault();
          }
        }

        if (a.hour.on) {
          if (d3.event.keyCode == 38) {
            if (
              a.scrolMove(a.hour.scrolposition - 1, a.hour, a.chartConfig.hour)
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 40) {
            if (
              a.scrolMove(a.hour.scrolposition + 1, a.hour, a.chartConfig.hour)
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 34 || d3.event.keyCode == 32) {
            if (
              a.scrolMove(
                a.hour.scrolposition + a.chartConfig.hour.extrapolation,
                a.hour,
                a.chartConfig.hour
              )
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 33) {
            if (
              a.scrolMove(
                a.hour.scrolposition - a.chartConfig.hour.extrapolation,
                a.hour,
                a.chartConfig.hour
              )
            )
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 35) {
            if (a.scrolMove(a.hour.scrolMax, a.hour, a.chartConfig.hour))
              d3.event.preventDefault();
          } else if (d3.event.keyCode == 36) {
            if (a.scrolMove(0, a.hour, a.chartConfig.hour))
              d3.event.preventDefault();
          }
        }
      });

      return this;
    }
  }

  drawChart(chart, chartConfig) {
    const a = this;

    chart.backscrol
      .attr("fill", "#fff")
      .attr("width", this.size * 7)
      .attr("height", this.size * chart.height);

    chart.verticalRange = [0, chart.domain.length * chart.size];
    chart.vertical = d3
      .scaleBand()
      .rangeRound(chart.verticalRange)
      .domain(chart.domain)
      .padding(a.chartConfig.layout.padding);
    chart.size2 =
      chart.vertical(chart.vertical.domain()[1]) -
      chart.vertical(chart.vertical.domain()[0]);

    const max = d3.max(chart.data, (d) => d.value);
    const min = d3.min(chart.data, (d) => d.value);
    const den = max - min;
    const color = (value) => (value === 0 ? 0 : 0.1 + (value - min) / den);

    chart.rects.transition().duration(200).attr("opacity", 0);

    if (!this.chartConfig.svg) {
      chart.svg.attr("width", a.width).attr("height", a.height);
    }

    chart.g.attr(
      "transform",
      `translate(${chart.margin.left}, ${chart.margin.top})`
    );

    if (!chartConfig.axis.vertical.all) {
      chart.verticalAxis
        .transition()
        .transition(500)
        .call(d3.axisLeft(chart.vertical))
        .attr("font-size", a.font_size);

      if (!chartConfig.axis.vertical.lines) {
        chart.verticalAxis.selectAll("line").transition().remove();
        chart.verticalAxis.select("path").transition().remove();
      }
    }

    if (!chartConfig.axis.day.all) {
      chart.dayAxis
        .transition()
        .transition(500)
        .call(d3.axisTop(a.day))
        .attr("font-size", a.chartConfig.layout.font_size2);
      chart.dayAxis
        .selectAll("text")
        .attr("y", 0)
        .transition()
        .text((d, i) =>
          String.adjustLength(
            MyDate.weekName()[i],
            a.chartConfig.layout.font_size2,
            chart.vertical.bandwidth()
          )
        );

      if (!chartConfig.axis.day.lines) {
        chart.dayAxis.selectAll("line").transition().remove();
        chart.dayAxis.select("path").transition().remove();
      }
    }

    chart.rects.attr(
      "transform",
      (d, i) =>
        `translate(${a.day(MyDate.weekName()[d.dayOfWeek])}, ${chart.vertical(
          chart.verticalFunction(chart.domain, d)
        )})`
    );

    chart.rects
      .attr("fill", (d) => ((d.value - min) / den > 0.8 ? "#fff" : "#000"))
      .select("rect")
      .attr("rx", a.rCorner)
      .attr("ry", a.rCorner)
      .attr("width", a.day.bandwidth())
      .attr("height", chart.vertical.bandwidth())
      .attr("fill", (d) => chartConfig.colors(color(d.value) + 0.1));

    if (a.chartConfig.cornerLabel !== undefined) {
      chart.rects
        .select(".corner")
        .attr("font-size", a.font_size * 0.5)
        .text((d, i) => d3.textData(d, a.chartConfig.cornerLabel.text));
    }

    if (a.chartConfig.centerLabel !== undefined) {
      chart.rects
        .select(".center")
        .attr("font-size", a.font_size * 0.9)
        .attr("dy", a.font_size * 0.3 + chart.vertical.bandwidth() / 2)
        .attr("dx", chart.vertical.bandwidth() / 2)
        .text((d, i) =>
          String.adjustLength(
            d3.textData(d, a.chartConfig.centerLabel.text),
            a.font_size * 0.9,
            chart.vertical.bandwidth(),
            true
          )
        );
    }

    if (chart.domain.length > chartConfig.extrapolation) {
      chart.extrapolation = true;

      const location = chartConfig.extrapolation * chart.size2;
      const location2 = (chartConfig.extrapolation + 1) * chart.size;

      chart.rects
        .transition()
        .delay(500)
        .duration(500)
        .attr("opacity", (d) => {
          if (
            chart.vertical(chart.verticalFunction(chart.domain, d)) > location
          ) {
            return 0;
          }

          return 1;
        })
        .attr("transform", (d) => {
          const temp = chart.vertical(chart.verticalFunction(chart.domain, d));

          if (temp > location2 || temp < -2 * chart.vertical.bandwidth()) {
            return `translate(${-3 * a.day.bandwidth()}, ${chart.vertical(
              chart.verticalFunction(chart.domain, d)
            )})`;
          }

          return `translate(${a.day(
            MyDate.weekName()[d.dayOfWeek]
          )}, ${chart.vertical(chart.verticalFunction(chart.domain, d))})`;
        });

      if (!chartConfig.axis.vertical.all) {
        chart.verticalTiks = chart.verticalAxis.selectAll(".tick");
        chart.verticalTiks
          .transition()
          .delay(500)
          .duration(500)
          .attr("opacity", (d) => {
            if (
              chart.vertical(chart.verticalFunction(chart.domain, d)) > location
            ) {
              return 0;
            }

            return 1;
          })
          .attr("transform", (d) => {
            const temp = chart.vertical(
              chart.verticalFunction(chart.domain, d)
            );

            if (temp > location2 || temp < -2 * chart.vertical.bandwidth()) {
              return `translate(${-2 * a.day.bandwidth()}, ${
                chart.vertical(chart.verticalFunction(chart.domain, d)) +
                chart.vertical.bandwidth() / 2
              })`;
            }

            return `translate(0, ${
              chart.vertical(chart.verticalFunction(chart.domain, d)) +
              chart.vertical.bandwidth() / 2
            })`;
          });
      }

      this.scrolEvents(chart, chartConfig);
    } else {
      chart.rects.transition().delay(500).duration(500).attr("opacity", 1);
    }
  }

  scrolEvents(chart, chartConfig) {
    const a = this;

    chart.extTriangles.attr(
      "transform",
      `translate(${-chart.margin.left / 2}, ${chart.vertical(
        chart.vertical.domain()[0]
      )})`
    );

    const y =
      chart.vertical(chart.domain[0]) +
      chartConfig.extrapolation * chart.size2 -
      0.25 * chart.size2;
    const yu = chart.vertical(chart.vertical.domain()[0]) - chart.size2 * 0.25;

    const seta = function (position) {
      let ret = [];

      if (position === 1) {
        ret = [
          { x: 0, y: y + 0.25 * chart.size2 },
          { x: -a.size / 3, y: y },
          { x: a.size / 3, y: y },
        ];
      } else {
        ret = [
          { x: 0, y: yu - 0.25 * chart.size2 },
          { x: -a.size / 3, y: yu },
          { x: a.size / 3, y: yu },
        ];
      }

      return ret;
    };

    const lineFunction = d3
      .line()
      .x((d) => d.x)
      .y((d) => d.y)
      .curve(d3.curveLinearClosed);

    chart.extTriangles
      .select(".up")
      .attr("opacity", 0)
      .attr("d", lineFunction(seta(0)))
      .attr("stroke", chartConfig.colors(0.5))
      .attr("stroke-width", 2)
      .attr("fill", chartConfig.colors(0.5));

    chart.extTriangles
      .select(".down")
      .attr("opacity", 0)
      .attr("d", lineFunction(seta(1)))
      .attr("stroke", chartConfig.colors(0.5))
      .attr("stroke-width", 2)
      .attr("fill", chartConfig.colors(0.5));

    chart.extTriangles
      .select(".down")
      .transition()
      .duration(500)
      .attr("opacity", 1);

    chart.scrolposition = 0;
    chart.scrolMax = chart.domain.length - chartConfig.extrapolation;

    const build = function (d) {
      if (
        d3.event.sourceEvent === undefined ||
        d3.event.sourceEvent.deltaY === undefined
      )
        return;

      const param = d3.event.sourceEvent.deltaY > 0 ? 1 : -1;

      a.scrolMove(chart.scrolposition + param, chart, chartConfig);
    };

    const zoom = d3.zoom().on("zoom", build);

    chart.scrol.call(zoom);

    chart.on = false;
    chart.g.on("mouseover", function (d) {
      chart.on = true;
    });
    chart.g.on("mouseout", function (d) {
      chart.on = false;
    });

    chart.extTriangles.selectAll("path").on("click", function (d) {
      const element = d3.select(this);

      if (element.attr("class") === "up") {
        a.scrolMove(chart.scrolposition - 1, chart, chartConfig);
      } else if (element.attr("class") === "down") {
        a.scrolMove(chart.scrolposition + 1, chart, chartConfig);
      }
    });
  }

  scrolMove(position, chart, chartConfig) {
    const a = this;

    if (chart.extrapolation) {
      if (chart.scrolposition === position) {
        return false;
      }

      chart.scrolposition = position;
      chart.scrolposition =
        chart.scrolposition > chart.scrolMax
          ? chart.scrolMax
          : chart.scrolposition;
      chart.scrolposition = chart.scrolposition < 0 ? 0 : chart.scrolposition;

      const location = chartConfig.extrapolation * chart.size2;
      const location2 = (chartConfig.extrapolation + 1) * chart.size;

      chart.extTriangles
        .select(".up")
        .attr("opacity", chart.scrolposition === 0 ? 0 : 1);
      chart.extTriangles
        .select(".down")
        .attr("opacity", chart.scrolposition === chart.scrolMax ? 0 : 1);

      chart.rects.attr("transform", function (d) {
        return `translate(${a.day(
          MyDate.weekName()[d.dayOfWeek]
        )}, ${chart.vertical(chart.verticalFunction(chart.domain, d))})`;
      });

      if (!chartConfig.axis.vertical.all) {
        chart.verticalAxis.selectAll(".tick").attr("transform", function (d) {
          const temp = chart.vertical(chart.verticalFunction(chart.domain, d));

          if (temp > location2 || temp < -2 * chart.vertical.bandwidth()) {
            return `translate(${-2 * a.day.bandwidth()}, ${
              chart.vertical(chart.verticalFunction(chart.domain, d)) +
              chart.vertical.bandwidth() / 2
            })`;
          }

          return `translate(0, ${
            chart.vertical(chart.verticalFunction(chart.domain, d)) +
            chart.vertical.bandwidth() / 2
          })`;
        });
      }

      chart.vertical.rangeRound(
        chart.verticalRange.map((d) => d - chart.scrolposition * chart.size2)
      );

      if (!chartConfig.axis.vertical.all) {
        chart.verticalAxis
          .transition()
          .duration(500)
          .call(d3.axisLeft(chart.vertical))
          .attr("font-size", a.font_size)
          .selectAll(".tick")
          .attr("opacity", function (d) {
            const temp = chart.vertical(
              chart.verticalFunction(chart.domain, d)
            );

            if (temp > location || temp < 0) {
              return 0;
            }

            return 1;
          })
          .attr("transform", function (d) {
            const temp = chart.vertical(
              chart.verticalFunction(chart.domain, d)
            );

            if (temp > location2 || temp < -2 * chart.vertical.bandwidth()) {
              return `translate(${-2 * a.day.bandwidth()}, ${
                chart.vertical(chart.verticalFunction(chart.domain, d)) +
                chart.vertical.bandwidth() / 2
              })`;
            }

            return `translate(0, ${
              chart.vertical(chart.verticalFunction(chart.domain, d)) +
              chart.vertical.bandwidth() / 2
            })`;
          });

        if (!chartConfig.axis.vertical.lines) {
          chart.verticalAxis.selectAll("line").remove();
          chart.verticalAxis.select("path").remove();
        }
      }

      chart.rects
        .transition()
        .duration(500)
        .attr("transform", function (d, i) {
          return `translate(${a.day(
            MyDate.weekName()[d.dayOfWeek]
          )}, ${chart.vertical(chart.verticalFunction(chart.domain, d))})`;
        })
        .attr("opacity", function (d) {
          const temp = chart.vertical(chart.verticalFunction(chart.domain, d));

          if (temp > location || temp < 0) {
            return 0;
          }

          return 1;
        });

      chart.rects
        .transition()
        .delay(550)
        .attr("transform", function (d) {
          const temp = chart.vertical(chart.verticalFunction(chart.domain, d));

          if (temp > location2 || temp < -2 * chart.vertical.bandwidth()) {
            return `translate(${-3 * a.day.bandwidth()}, ${chart.vertical(
              chart.verticalFunction(chart.domain, d)
            )})`;
          }

          return `translate(${a.day(
            MyDate.weekName()[d.dayOfWeek]
          )}, ${chart.vertical(chart.verticalFunction(chart.domain, d))})`;
        });

      return true;
    }

    return false;
  }

  hourView() {
    const a = this;

    if (!a.chartConfig.chart.hour) {
      const icon = function (position) {
        let ret = [];

        if (position) {
          ret = d3.path.icons.arrow_down(a.size * 0.4);
        } else {
          ret = d3.path.icons.arrow_right(a.size * 0.4);
        }

        return ret;
      };

      const lineFunction = d3.path.lineFunction(d3.curveLinearClosed);

      if (a.hour.hourShow) {
        a.hour.rects
          .transition()
          .delay(0)
          .duration(500)
          .attr(
            "transform",
            (d) =>
              `translate(${a.day(MyDate.weekName()[d.dayOfWeek])}, ${
                a.hour.vertical(
                  a.hour.vertical.domain()[
                    a.hour.scrolposition ? a.hour.scrolposition : 0
                  ]
                ) - a.hour.size2
              })`
          )
          .attr("opacity", 0);

        if (!a.chartConfig.hour.axis.vertical.all) {
          a.hour.verticalAxis
            .selectAll(".tick")
            .transition()
            .delay(0)
            .duration(500)
            .attr(
              "transform",
              (d) =>
                `translate(0, ${
                  a.hour.vertical(
                    a.hour.vertical.domain()[
                      a.hour.scrolposition ? a.hour.scrolposition : 0
                    ]
                  ) -
                  a.hour.size2 / 2
                })`
            )
            .attr("opacity", 0);
        }

        if (a.hour.extrapolation) {
          a.hour.extTriangles
            .selectAll("path")
            .transition()
            .delay(0)
            .duration(500)
            .attr("opacity", 0);
        }
      } else {
        const location = a.chartConfig.hour.extrapolation * a.hour.size2;
        const location2 = (a.chartConfig.hour.extrapolation + 1) * a.hour.size;

        a.hour.rects
          .transition()
          .transition(500)
          .attr(
            "transform",
            (d, i) =>
              `translate(${a.day(
                MyDate.weekName()[d.dayOfWeek]
              )}, ${a.hour.vertical(
                a.hour.verticalFunction(a.hour.domain, d)
              )})`
          )
          .attr("opacity", (d) => {
            const temp = a.hour.vertical(
              a.hour.verticalFunction(a.hour.domain, d)
            );

            if (temp > location || temp < 0) {
              return 0;
            }

            return 1;
          });

        if (!a.chartConfig.hour.axis.vertical.all) {
          a.hour.verticalAxis
            .selectAll(".tick")
            .transition()
            .duration(500)
            .attr("opacity", (d) => {
              const temp = a.hour.vertical(
                a.hour.verticalFunction(a.hour.domain, d)
              );

              if (temp > location || temp < 0) {
                return 0;
              }

              return 1;
            })
            .attr("transform", (d) => {
              const temp = a.hour.vertical(
                a.hour.verticalFunction(a.hour.domain, d)
              );

              if (temp > location2 || temp < -2 * a.hour.vertical.bandwidth()) {
                return `translate(${-2 * a.day.bandwidth()}, ${
                  a.hour.vertical(a.hour.verticalFunction(a.hour.domain, d)) +
                  a.hour.vertical.bandwidth() / 2
                })`;
              }

              return `translate(0, ${
                a.hour.vertical(a.hour.verticalFunction(a.hour.domain, d)) +
                a.hour.vertical.bandwidth() / 2
              })`;
            });
        }

        if (a.hour.extrapolation) {
          a.hour.extTriangles
            .select(".down")
            .attr("opacity", a.hour.scrolposition === a.hour.scrolMax ? 0 : 1);
        }
      }

      a.hour.hourShow = !a.hour.hourShow;
      a.hour.collapse
        .select("path")
        .transition()
        .duration(500)
        .attr("d", lineFunction(icon(a.hour.hourShow)))
        .attr(
          "transform",
          `translate(${a.day(a.day.domain()[0]) + a.day.bandwidth() * 0.5}, ${
            a.size * 0.3
          })`
        );
    }
  }

  dataSetter() {
    const a = this;

    a.data = a.chartConfig.data;
    a.data = a.data.map((d) => {
      d.year = $(d).attr(a.chartConfig.dataConfig.year);
      d.month = $(d).attr(a.chartConfig.dataConfig.month);
      d.day = $(d).attr(a.chartConfig.dataConfig.day);
      d.hour = $(d).attr(a.chartConfig.dataConfig.hour);
      d.value = $(d).attr(a.chartConfig.dataConfig.value);
      d.dayOfWeek = MyDate.dayOfWeek(d);

      return d;
    });

    this.chartConfig.data = a.data.sort(MyDate.greatThan);

    if (!a.chartConfig.chart.hour) {
      a.hour.totalData = [];

      for (let i = 0; i < 7; i++) {
        a.hour.totalData[i] = {};
        a.hour.totalData[i].value = 0;
        a.hour.totalData[i].dayOfWeek = i;

        this.hour.totalData[i].toString = function () {
          return MyDate.weekName(this.dayOfWeek);
        };
      }

      this.hour.data = [];
      const model = a.chartConfig.hour.model === 4 ? 4 : 24;

      for (let i = 0; i < 7 * model; i++) {
        this.hour.data[i] = {};
        this.hour.data[i].value = 0;
        this.hour.data[i].dayOfWeek = parseInt(i / model);

        if (model === 4) {
          this.hour.data[i].hour = (i % 4) * 6;
          this.hour.data[i].hour = `${this.hour.data[i].hour < 10 ? "0" : ""}${
            this.hour.data[i].hour
          }h-${this.hour.data[i].hour + 6 < 10 ? "0" : ""}${
            this.hour.data[i].hour + 6
          }h`;
        } else {
          this.hour.data[i].hour = i % model;
        }

        this.hour.data[i].toString = function () {
          return `${MyDate.weekName(this.dayOfWeek)},${MyDate.dayVal(
            MyDate.hourNames(undefined, model),
            this
          )}`;
        };
      }

      const users_set = new Set();

      for (let i = 0; i < a.data.length; i++) {
        const obj = `${a.data[i].dayOfWeek.toString()}-${a.data[
          i
        ].user_id.toString()}`;

        if (!users_set.has(obj)) {
          users_set.add(obj);

          a.hour.totalData[a.data[i].dayOfWeek].value += a.data[i].value;

          if (a.chartConfig.hour.model === 4) {
            this.hour.data[
              a.data[i].dayOfWeek * 4 + parseInt(a.data[i].hour / 6)
            ].value += a.data[i].value;
          } else {
            this.hour.data[a.data[i].dayOfWeek * 24 + a.data[i].hour].value +=
              a.data[i].value;
          }
        }
      }
    }

    if (!a.chartConfig.chart.calendar) {
      if (a.chartConfig.dataConfig.init === undefined) {
        a.chartConfig.dataConfig.init = {};
      }
      if (a.chartConfig.dataConfig.init.year === undefined) {
        a.chartConfig.dataConfig.init.year = a.data[0].year;
      }
      if (a.chartConfig.dataConfig.init.month === undefined) {
        a.chartConfig.dataConfig.init.month = a.data[0].month;
      }
      if (a.chartConfig.dataConfig.init.day === undefined) {
        a.chartConfig.dataConfig.init.day = a.data[0].day;
      }

      if (a.chartConfig.dataConfig.end === undefined) {
        a.chartConfig.dataConfig.end = {};
      }
      if (a.chartConfig.dataConfig.end.year === undefined) {
        a.chartConfig.dataConfig.end.year = a.data[a.data.length - 1].year;
      }
      if (a.chartConfig.dataConfig.end.month === undefined) {
        a.chartConfig.dataConfig.end.month = a.data[a.data.length - 1].month;
      }
      if (a.chartConfig.dataConfig.end.day === undefined) {
        a.chartConfig.dataConfig.end.day = a.data[a.data.length - 1].day;
      }

      a.chartConfig.dataConfig.init = new MyDate(
        a.chartConfig.dataConfig.init.year,
        a.chartConfig.dataConfig.init.month,
        a.chartConfig.dataConfig.init.day
      );

      a.chartConfig.dataConfig.end = new MyDate(
        a.chartConfig.dataConfig.end.year,
        a.chartConfig.dataConfig.end.month,
        a.chartConfig.dataConfig.end.day
      );

      this.calendar.data = [];

      const start = a.chartConfig.dataConfig.init;
      const end = a.chartConfig.dataConfig.end;

      const years = end.year - start.year + 1;
      const months = 12 * (years - 1) + end.month - start.month + 1;
      let j = new MyDate(0, 0, 0, 0, 0);
      let offset = new MyDate(0, 1, 0, 0, 0);
      let days = [];
      let indexData = 0;
      let i = 0;

      for (
        i, j = MyDate.sum(j, start);
        i < months;
        i++, j = MyDate.sum(j, offset)
      ) {
        if (i === 0) {
          days[i] = MyDate.nDays(j) - start.day + 1;
          j.day = start.day;
        } else if (i === months - 1) {
          days[i] = end.day;
          j.day = 1;
        } else {
          days[i] = MyDate.nDays(j);
          j.day = 1;
        }

        let ofset = new MyDate(0, 0, 1, 0, 0);
        let k = 0;

        for (j.value = 0; k < days[i]; k++) {
          j.dayOfWeek = MyDate.dayOfWeek(j);

          while (
            a.data[indexData] &&
            MyDate.greatThan(a.data[indexData], j, true) === 0
          ) {
            j.value += a.data[indexData].value;
            indexData++;
          }

          this.calendar.data.push(
            new MyDate(j.year, j.month, j.day, undefined, j.value, j.dayOfWeek)
          );

          if (k !== days[i] - 1) {
            j = MyDate.sum(j, ofset);
          } else {
            j.day = 1;
          }
        }
      }
    }

    return this;
  }

  resize(width, height) {
    if (width !== undefined) {
      this.chartConfig.dimensions.width = width;
    }

    if (height !== undefined) {
      this.chartConfig.dimensions.height = height;
    }

    return this.draw();
  }

  weekDomain(model) {
    switch (model) {
      case 4:
      case 12:
      case 24:
        return MyDate.hourNames(undefined, model);
      default:
        const a = this;

        const start = a.calendar.data[0];
        const end = a.calendar.data[a.calendar.data.length - 1];
        const domain = [
          new MyDate(start.year, start.month, start.day - start.dayOfWeek),
        ];

        while (MyDate.greatThan(domain[domain.length - 1], end) <= 0) {
          domain.push(MyDate.sum(domain[domain.length - 1], { day: 7 }));
        }

        domain.pop();

        return domain;
    }
  }

  titleConstruct() {
    const a = this;
    const b = JSON.copyObject(a.chartConfig.dataConfig);

    b.init.month = MyDate.monthName(b.init.month);
    b.end.month = MyDate.monthName(b.end.month);

    if (a.chartConfig.title !== undefined) {
      if (this.titleElement === undefined) {
        this.titleElement = this.svg
          .append("text")
          .attr("id", `titleElement_${this.chartConfig.name}`)
          .style("font-size", a.chartConfig.title.font.size)
          .style("font-family", a.chartConfig.title.font.name)
          .attr("fill", "#fff")
          .text(() =>
            d3.textData(a.chartConfig.dataConfig, a.chartConfig.title.text)
          );
      }

      this.titleElement.style(
        "font-size",
        String.adjustWidth(
          this.titleElement.text(),
          a.chartConfig.title.font.size,
          a.width
        )
      );

      a.chartConfig.title.position.dy =
        parseInt(this.titleElement.style("font-size").replace("px", "")) / 3;

      const labelDim = document.getDimensions(
        `#titleElement_${this.chartConfig.name}`
      );

      this.titleElement.attr("transform", () => {
        if (a.chartConfig.title.position.align === "middle") {
          return `translate(${a.width / 2 - labelDim.w / 2}, ${
            (2 * labelDim.h) / 3
          })`;
        } else if (a.chartConfig.title.position.align === "end") {
          return `translate(${a.width - labelDim.w}, ${(2 * labelDim.h) / 3})`;
        } else {
          return `translate(4, ${(2 * labelDim.h) / 3})`;
        }
      });

      const titleD = document.getDimensions(
        `#titleElement_${this.chartConfig.name}`
      );

      a.chartConfig.title.desloc = titleD.h;
    }

    return this;
  }

  toolTipConstruct() {
    const a = this;

    if (this.chartConfig.tooltip !== undefined) {
      this.toolTip = new ToolTip(this.chartConfig.tooltip);

      a.chartConfig.interactions.mouseover.push((element, data) => {
        element = d3.select(element);

        if (element.attr("opacity") !== 0) {
          a.toolTip.show(data);
        }
      });

      a.chartConfig.interactions.mousemove.push((element, data) =>
        a.toolTip.move()
      );
      a.chartConfig.interactions.mouseout.push((element, data) =>
        a.toolTip.hide()
      );
    }

    return this;
  }

  addInteractions() {
    const a = this;

    a.chartConfig.interactions.mouseover.push((element, data) => {
      const currentEl = d3.select(element).select("rect");

      currentEl.attr("opacity", 0.8);
      currentEl
        .attr("stroke-width", "3")
        .attr("stroke", a.chartConfig.layout.colors(0.5));
    });

    a.chartConfig.interactions.mouseout.push((element, data) => {
      const currentEl = d3.select(element).select("rect");

      currentEl.attr("opacity", 1);
      currentEl
        .attr("stroke-width", "0")
        .attr("stroke", a.chartConfig.layout.colors(0));
    });

    d3.addEvents(a.calendar.rects, a.chartConfig.interactions);
    d3.addEvents(a.hour.rects, a.chartConfig.interactions);
    d3.addEvents(a.hour.totalRects, a.chartConfig.interactions);

    $("#panel_loading_mask5").hide();
    return this;
  }
}

$(function () {
  const dataUrl = $(".heatmap").data("url");

  let catId = $("#categoriesSelect").val();

  if (catId !== undefined) {
    heatmapData(dataUrl, $("#from").val(), $("#until").val(), 0, catId);
  } else {
    heatmapData(dataUrl, $("#from").val(), $("#until").val());
  }
});

function heatmapData(url, dataIni, dataEnd, option = 0, category = 0) {
  $.get(url, { data_ini: dataIni, data_end: dataEnd, category: category }, (dataset) => {
    let dataConfig = {};
    if (option == 5) {
      dataset = dataset.filter((d) => d.teacher == 1);
    }
    if (option == 4) {
      dataset = dataset.filter((d) => d.teacher == 0);
    }
    if (dataset.length > 0) {
      dataConfig = {
        init: {
          year: dataset[0].year,
          month: dataset[0].month,
          day: dataset[0].day,
        },
        end: {
          year: dataset[dataset.length - 1].year,
          month: dataset[dataset.length - 1].month,
          day: dataset[dataset.length - 1].day,
        },
      };
    }

    $("#studentsHeatMap").prop("checked", true);
    $("#teachersHeatMap").prop("checked", true);
    $("#generalHeatMap").prop("checked", true);

    chartConfig = {
      parent: ".heatmap_chart",
      data: dataset,
      dataConfig: dataConfig,
      dimensions: {
        width: 360,
        height: 500,
      },
      tooltip: {
        text: "<value> usuários distintos\r\n Dia: <this>",
      },
    };

    heatmap = new HeatMap(chartConfig);
    document.getElementsByName("radio-heatmap").forEach(function (e) {
      e.addEventListener("click", function () {
        let showStudents = $("#studentsHeatMap").prop("checked"),
          showTeachers = $("#teachersHeatMap").prop("checked"),
          showCoordinators = $("#generalHeatMap").prop("checked");

        $(".heatmap .heatmap_chart").html("");

        let data = [];

        if (showStudents && showTeachers && showCoordinators) {
          data = dataset;
        } else if (!showStudents && !showTeachers && !showCoordinators) {
          data = dataset;

          $("#studentsHeatMap").prop("checked", true);
          $("#teachersHeatMap").prop("checked", true);
          $("#generalHeatMap").prop("checked", true);
        } else if (!showStudents && showTeachers && showCoordinators) {
          data = dataset.filter((d) => d.teacher !== 0);
        } else if (showStudents && !showTeachers && showCoordinators) {
          data = dataset.filter((d) => d.teacher !== 1);
        } else if (showStudents && showTeachers && !showCoordinators) {
          data = dataset.filter((d) => d.teacher !== 2);
        } else if (!showStudents && !showTeachers && showCoordinators) {
          data = dataset.filter((d) => d.teacher === 2);
        } else if (!showStudents && showTeachers && !showCoordinators) {
          data = dataset.filter((d) => d.teacher === 1);
        } else if (showStudents && !showTeachers && !showCoordinators) {
          data = dataset.filter((d) => d.teacher === 0);
        }

        if (data.length > 0) {
          dataConfig = {
            init: {
              year: data[0].year,
              month: data[0].month,
              day: data[0].day,
            },
            end: {
              year: data[data.length - 1].year,
              month: data[data.length - 1].month,
              day: data[data.length - 1].day,
            },
          };
        }

        chartConfig = {
          parent: ".heatmap_chart",
          data: data,
          dataConfig: dataConfig,
          dimensions: {
            width: 360,
            height: 500,
          },
          tooltip: {
            text: "<value> usuários distintos\r\n Dia: <this>",
          },
        };

        heatmap = new HeatMap(chartConfig);
      });
    });
  });
}
