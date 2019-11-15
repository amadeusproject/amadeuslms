/**
 * Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 *
 * Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 *
 * O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 *
 * Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 *
 * Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
 */

let calendarCount = 0;

class HeatMap {
  constructor(chartConfig) {
    this.validData(chartConfig)
      .create()
      .draw()
      .addInteractions();
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
    if (a.chartConfig.dataConfig.year === undefined) a.chartConfig.dataConfig.year = "year";
    if (a.chartConfig.dataConfig.month === undefined) a.chartConfig.dataConfig.month = "month";
    if (a.chartConfig.dataConfig.day === undefined) a.chartConfig.dataConfig.day = "day";
    if (a.chartConfig.dataConfig.hour === undefined) a.chartConfig.dataConfig.hour = "hour";
    if (a.chartConfig.dataConfig.dayOfWeek === undefined) a.chartConfig.dataConfig.dayOfWeek = "dayOfWeek";
    if (a.chartConfig.dataConfig.value === undefined) a.chartConfig.dataConfig.value = "value";

    if (a.chartConfig.name === undefined || a.chartConfig.name === `CalendarHeatMap${calendarCount - 1}`) {
      a.chartConfig.name = `CalendarHeatMap${calendarCount++}`;
    }
    if (a.chartConfig.parent === undefined) {
      a.chartConfig.parent = "body";
      a.chartConfig.svg = false;
    }
    if (a.chartConfig.svg === undefined) a.chartConfig.svg = false;

    if (a.chartConfig.dimensions === undefined) a.chartConfig.dimensions = {};
    if (a.chartConfig.dimensions.width === undefined) a.chartConfig.dimensions.width = 360;
    if (a.chartConfig.dimensions.height === undefined) a.chartConfig.dimensions.height = 600;

    if (a.chartConfig.layout === undefined) a.chartConfig.layout = {};
    if (a.chartConfig.layout.corner === undefined) a.chartConfig.layout.corner = 0.1;
    if (a.chartConfig.layout.padding === undefined) a.chartConfig.layout.padding = 0.1;
    if (a.chartConfig.layout.margin === undefined) a.chartConfig.layout.margin = {};
    if (a.chartConfig.layout.margin.top === undefined) a.chartConfig.layout.margin.top = 20;
    if (a.chartConfig.layout.margin.right === undefined) a.chartConfig.layout.margin.right = 20;
    if (a.chartConfig.layout.margin.bottom === undefined) a.chartConfig.layout.margin.bottom = 50;
    if (a.chartConfig.layout.margin.left === undefined) a.chartConfig.layout.margin.left = 50;
    if (a.chartConfig.layout.extrapolation === undefined) a.chartConfig.layout.extrapolation = 5;
    if (a.chartConfig.layout.colors === undefined) a.chartConfig.layout.colors = d3.interpolateGreens;
    if (a.chartConfig.layout.font_size === undefined) a.chartConfig.layout.font_size = 20;
    if (a.chartConfig.layout.font_size2 === undefined) a.chartConfig.layout.font_size2 = a.chartConfig.layout.font_size;

    a.calendar = {};
    if (!a.chartConfig.chart.calendar) {
      if (a.chartConfig.calendar === undefined) a.chartConfig.calendar = {};
      if (a.chartConfig.calendar.svg === undefined) a.chartConfig.calendar.svg = true;
      if (a.chartConfig.calendar.parent === undefined && a.chartConfig.calendar.svg != true) {
        a.chartConfig.calendar.parent = a.chartConfig.parent;
        a.chartConfig.calendar.svg = a.chartConfig.svg;
      }
      if (a.chartConfig.calendar.margin === undefined) a.chartConfig.calendar.margin = {};
      if (a.chartConfig.calendar.margin.top === undefined)
        a.chartConfig.calendar.margin.top = a.chartConfig.layout.margin.top;
      if (a.chartConfig.calendar.margin.right === undefined)
        a.chartConfig.calendar.margin.right = a.chartConfig.layout.margin.right;
      if (a.chartConfig.calendar.margin.bottom === undefined)
        a.chartConfig.calendar.margin.bottom = a.chartConfig.layout.margin.bottom;
      if (a.chartConfig.calendar.margin.left === undefined)
        a.chartConfig.calendar.margin.left = a.chartConfig.layout.margin.left;

      if (a.chartConfig.calendar.extrapolation === undefined)
        a.chartConfig.calendar.extrapolation = a.chartConfig.layout.extrapolation;
      if (a.chartConfig.calendar.extrapolation < 1) a.chartConfig.calendar.extrapolation = 1;
      if (a.chartConfig.calendar.axis === undefined) a.chartConfig.axis = {};
      if (a.chartConfig.calendar.axis.vertical === undefined) a.chartConfig.calendar.axis.vertical = {};
      if (a.chartConfig.calendar.axis.day === undefined) a.chartConfig.calendar.axis.day = {};
      if (a.chartConfig.calendar.colors === undefined) a.chartConfig.calendar.colors = a.chartConfig.layout.colors;
      if (a.chartConfig.calendar.texts === undefined) a.chartConfig.calendar.texts = {};
    } else {
      a.chartConfig.calendar = undefined;
    }

    a.hour = {};
    if (!a.chartConfig.chart.hour) {
      if (a.chartConfig.hour === undefined) a.chartConfig.hour = {};
      if (a.chartConfig.hour.svg === undefined) a.chartConfig.hour.svg = true;
      if (a.chartConfig.hour.parent === undefined && a.chartConfig.hour.svg != true) {
        a.chartConfig.hour.parent = a.chartConfig.parent;
        a.chartConfig.hour.svg = a.chartConfig.svg;
      }

      if (
        a.chartConfig.hour.model === undefined ||
        (a.chartConfig.hour.model != 12 && a.chartConfig.hour.model != 24)
      ) {
        a.chartConfig.hour.model = 4;
      }

      if (a.chartConfig.hour.margin === undefined) a.chartConfig.hour.margin = {};
      if (a.chartConfig.hour.margin.top === undefined) a.chartConfig.hour.margin.top = a.chartConfig.layout.margin.top;
      if (a.chartConfig.hour.margin.right === undefined)
        a.chartConfig.hour.margin.right = a.chartConfig.layout.margin.right;
      if (a.chartConfig.hour.margin.bottom === undefined)
        a.chartConfig.hour.margin.bottom = a.chartConfig.layout.margin.bottom;
      if (a.chartConfig.hour.margin.left === undefined)
        a.chartConfig.hour.margin.left = a.chartConfig.layout.margin.left;

      if (a.chartConfig.hour.extrapolation === undefined)
        a.chartConfig.hour.extrapolation = a.chartConfig.hour.extrapolation;

      a.chartConfig.hour.extrapolation--;

      if (a.chartConfig.hour.extrapolation < 1) a.chartConfig.hour.extrapolation = 1;
      if (a.chartConfig.hour.axis === undefined) a.chartConfig.hour.axis = {};
      if (a.chartConfig.hour.axis.vertical === undefined) a.chartConfig.hour.vertical = {};
      if (a.chartConfig.hour.axis.day === undefined) a.chartConfig.hour.axis.day = {};
      if (a.chartConfig.hour.colors === undefined) a.chartConfig.hour.colors = d3.interpolateGreys;
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
        if (a.chartConfig.cornerLabel.color === undefined) a.chartConfig.cornerLabel.color = "#fff";
        if (a.chartConfig.cornerLabel.font === undefined) a.chartConfig.cornerLabel.font = {};
        if (a.chartConfig.cornerLabel.font.name === undefined) a.chartConfig.cornerLabel.font.name = "sans-serif";
        if (a.chartConfig.cornerLabel.font.size === undefined) a.chartConfig.cornerLabel.font.size = 12;
        if (a.chartConfig.cornerLabel.position === undefined) a.chartConfig.cornerLabel.position = {};
        if (a.chartConfig.cornerLabel.position.dx === undefined) a.chartConfig.cornerLabel.position.dx = 0;
        if (a.chartConfig.cornerLabel.position.dy === undefined) a.chartConfig.cornerLabel.position.dy = 0;
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
        if (a.chartConfig.centerLabel.color === undefined) a.chartConfig.centerLabel.color = "#fff";
        if (a.chartConfig.centerLabel.font === undefined) a.chartConfig.centerLabel.font = {};
        if (a.chartConfig.centerLabel.font.name === undefined) a.chartConfig.centerLabel.font.name = "sans-serif";
        if (a.chartConfig.centerLabel.font.size === undefined) a.chartConfig.centerLabel.font.size = 12;
        if (a.chartConfig.centerLabel.position === undefined) a.chartConfig.centerLabel.position = {};
        if (a.chartConfig.centerLabel.position.dx === undefined) a.chartConfig.centerLabel.position.dx = 0;
        if (a.chartConfig.centerLabel.position.dy === undefined) a.chartConfig.centerLabel.position.dy = 0;
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
}
