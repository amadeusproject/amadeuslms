var calendarHeatMapCont = 0;

class CalendarHeatMap {
    constructor(chartConfig) {
        this.validData(chartConfig).create().draw().addInteractions();
    }
    validData(chartConfig) {
        var a = this;
        this.chartConfig = chartConfig;

        if (a.chartConfig.data == undefined) {//informations to create chart
            console.error("Impossible create CalendarHeatMap without DataSource");
            return;
        }

        if(a.chartConfig.chart==undefined)a.chartConfig.chart = {};//set calendar true to hide calendar and hour true to hide hour chart

        if (a.chartConfig.dataConfig == undefined) a.chartConfig.dataConfig = {};//configurations of dataset
        if (a.chartConfig.dataConfig.year == undefined) a.chartConfig.dataConfig.year = "year";
        if (a.chartConfig.dataConfig.month == undefined) a.chartConfig.dataConfig.month = "month";
        if (a.chartConfig.dataConfig.day == undefined) a.chartConfig.dataConfig.day = "day";
        if (a.chartConfig.dataConfig.hour == undefined) a.chartConfig.dataConfig.hour = "hour";
        if (a.chartConfig.dataConfig.dayOfWeek == undefined) a.chartConfig.dataConfig.dayOfWeek = "dayOfWeek";
        if (a.chartConfig.dataConfig.value == undefined) a.chartConfig.dataConfig.value = "value";

        if (a.chartConfig.chart == undefined) a.chartConfig.chart = {};//restrictions of visualizations

        //where create
        if (a.chartConfig.name == undefined || a.chartConfig.name == "CalendarHeatMap" + (calendarHeatMapCont - 1))
            a.chartConfig.name = "CalendarHeatMap" + calendarHeatMapCont++;
        if (a.chartConfig.parent == undefined) { a.chartConfig.parent = "body"; a.chartConfig.svg = false; }
        if (a.chartConfig.svg == undefined) a.chartConfig.svg = false;

        //dimensions of chart. This will be changed by code
        if (a.chartConfig.dimensions == undefined) a.chartConfig.dimensions = {};
        if (a.chartConfig.dimensions.width == undefined) a.chartConfig.dimensions.width = 400;
        if (a.chartConfig.dimensions.height == undefined) a.chartConfig.dimensions.height = 600;

        //Layout configs
        if (a.chartConfig.layout == undefined) a.chartConfig.layout = {};
        if (a.chartConfig.layout.corner == undefined) a.chartConfig.layout.corner = 0.1;//round corner of chart's rect
        if (a.chartConfig.layout.padding == undefined) a.chartConfig.layout.padding = 0.1;//space between chart's rect
        if (a.chartConfig.layout.margin == undefined) a.chartConfig.layout.margin = {};//space round chart's rect
        if (a.chartConfig.layout.margin.top == undefined) a.chartConfig.layout.margin.top = 20;
        if (a.chartConfig.layout.margin.right == undefined) a.chartConfig.layout.margin.right = 20;
        if (a.chartConfig.layout.margin.bottom == undefined) a.chartConfig.layout.margin.bottom = 50;
        if (a.chartConfig.layout.margin.left == undefined) a.chartConfig.layout.margin.left = 50;
        if (a.chartConfig.layout.extrapolation == undefined) a.chartConfig.layout.extrapolation = 5;
        if (a.chartConfig.layout.colors == undefined) a.chartConfig.layout.colors = d3.interpolateGreens;//function(d){return color} - d E [0,1];
        if (a.chartConfig.layout.font_size == undefined) a.chartConfig.layout.font_size = 20;	//font-size will be changed by code
        if (a.chartConfig.layout.font_size2 == undefined) a.chartConfig.layout.font_size2 = a.chartConfig.layout.font_size;	

        a.calendar = {};
        if (!a.chartConfig.chart.calendar) {
            if (a.chartConfig.calendar == undefined) a.chartConfig.calendar = {};
            if (a.chartConfig.calendar.svg == undefined) a.chartConfig.calendar.svg = true;
            if (a.chartConfig.calendar.parent == undefined && a.chartConfig.calendar.svg != true) {
                a.chartConfig.calendar.parent = a.chartConfig.parent;
                a.chartConfig.calendar.svg = a.chartConfig.svg;
            }
            if (a.chartConfig.calendar.margin == undefined) a.chartConfig.calendar.margin = {};//space round chart's rect
            if (a.chartConfig.calendar.margin.top == undefined) a.chartConfig.calendar.margin.top = a.chartConfig.layout.margin.top;
            if (a.chartConfig.calendar.margin.right == undefined) a.chartConfig.calendar.margin.right = a.chartConfig.layout.margin.right;
            if (a.chartConfig.calendar.margin.bottom == undefined) a.chartConfig.calendar.margin.bottom = a.chartConfig.layout.margin.bottom;
            if (a.chartConfig.calendar.margin.left == undefined) a.chartConfig.calendar.margin.left = a.chartConfig.layout.margin.left;

            if (a.chartConfig.calendar.extrapolation == undefined) a.chartConfig.calendar.extrapolation = a.chartConfig.layout.extrapolation;
            if (a.chartConfig.calendar.extrapolation < 1) a.chartConfig.calendar.extrapolation = 1;
            if (a.chartConfig.calendar.axis == undefined) a.chartConfig.calendar.axis = {};//restrictions os axis
            if (a.chartConfig.calendar.axis.vertical == undefined) a.chartConfig.calendar.axis.vertical = {};
            if (a.chartConfig.calendar.axis.day == undefined) a.chartConfig.calendar.axis.day = {};
            if (a.chartConfig.calendar.colors == undefined) a.chartConfig.calendar.colors = a.chartConfig.layout.colors;
            if (a.chartConfig.calendar.texts == undefined) a.chartConfig.calendar.texts = {};
        } else {
            a.chartConfig.calendar = undefined;
        }

        a.hour = {};
        if (!a.chartConfig.chart.hour) {
            if (a.chartConfig.hour == undefined) a.chartConfig.hour = {};
            if (a.chartConfig.hour.svg == undefined) a.chartConfig.hour.svg = true;
            if (a.chartConfig.hour.parent == undefined && a.chartConfig.hour.svg != true) {
                a.chartConfig.hour.parent = a.chartConfig.parent;
                a.chartConfig.hour.svg = a.chartConfig.svg;
            }

            if (a.chartConfig.hour.model == undefined || (a.chartConfig.hour.model != 12 && a.chartConfig.hour.model != 24))
                a.chartConfig.hour.model = 4;

            if (a.chartConfig.hour.margin == undefined) a.chartConfig.hour.margin = {};//space round chart's rect
            if (a.chartConfig.hour.margin.top == undefined) a.chartConfig.hour.margin.top = a.chartConfig.layout.margin.top;
            if (a.chartConfig.hour.margin.right == undefined) a.chartConfig.hour.margin.right = a.chartConfig.layout.margin.right;
            if (a.chartConfig.hour.margin.bottom == undefined) a.chartConfig.hour.margin.bottom = a.chartConfig.layout.margin.bottom;
            if (a.chartConfig.hour.margin.left == undefined) a.chartConfig.hour.margin.left = a.chartConfig.layout.margin.left;

            if (a.chartConfig.hour.extrapolation == undefined)
                a.chartConfig.hour.extrapolation = a.chartConfig.layout.extrapolation;
            a.chartConfig.hour.extrapolation--;
            if (a.chartConfig.hour.extrapolation < 1) a.chartConfig.hour.extrapolation = 1;
            if (a.chartConfig.hour.axis == undefined) a.chartConfig.hour.axis = {};//restrictions os axis
            if (a.chartConfig.hour.axis.vertical == undefined) a.chartConfig.hour.axis.vertical = {};
            if (a.chartConfig.hour.axis.day == undefined) a.chartConfig.hour.axis.day = {};
            if (a.chartConfig.hour.colors == undefined) a.chartConfig.hour.colors = d3.interpolateGreys;
            if (a.chartConfig.hour.texts == undefined) a.chartConfig.hour.texts = {};
        } else {
            a.chartConfig.hour = undefined;
        }

        a.chartConfig.title = d3.titleValid(a.chartConfig.title);//configuration pattern in JSUtil.js

        if (a.chartConfig.cornerLabel != undefined) {//Label in corner of chart's rect
            //Without a text, this label will not be created
            if (a.chartConfig.hour && a.chartConfig.hour.texts.corner == undefined && a.chartConfig.calendar && a.chartConfig.calendar.texts.corner == undefined)
                a.chartConfig.cornerLabel = undefined;
            else {
                if (a.chartConfig.cornerLabel.color == undefined) a.chartConfig.cornerLabel.color = "#FFF";
                if (a.chartConfig.cornerLabel.font == undefined) a.chartConfig.cornerLabel.font = {};
                if (a.chartConfig.cornerLabel.font.name == undefined) a.chartConfig.cornerLabel.font.name = "sans-serif";
                if (a.chartConfig.cornerLabel.font.size == undefined) a.chartConfig.cornerLabel.font.size = 12;
                if (a.chartConfig.cornerLabel.position == undefined) a.chartConfig.cornerLabel.position = {};
                if (a.chartConfig.cornerLabel.position.dx == undefined) a.chartConfig.cornerLabel.position.dx = 0;
                if (a.chartConfig.cornerLabel.position.dy == undefined) a.chartConfig.cornerLabel.position.dy = 0;
            }
        }
        if (a.chartConfig.centerLabel != undefined) {//Label in center of chart's rect
            //Without a text, this label will not be created
            if (a.chartConfig.hour && a.chartConfig.hour.texts.center == undefined && a.chartConfig.calendar && a.chartConfig.calendar.texts.center == undefined)
                a.chartConfig.centerLabel = undefined;
            else {
                if (a.chartConfig.centerLabel.color == undefined) a.chartConfig.centerLabel.color = "#FFF";
                if (a.chartConfig.centerLabel.font == undefined) a.chartConfig.centerLabel.font = {};
                if (a.chartConfig.centerLabel.font.name == undefined) a.chartConfig.centerLabel.font.name = "sans-serif";
                if (a.chartConfig.centerLabel.font.size == undefined) a.chartConfig.centerLabel.font.size = 12;
                if (a.chartConfig.centerLabel.position == undefined) a.chartConfig.centerLabel.position = {};
                if (a.chartConfig.centerLabel.position.dx == undefined) a.chartConfig.centerLabel.position.dx = 0;
                if (a.chartConfig.centerLabel.position.dy == undefined) a.chartConfig.centerLabel.position.dy = 0;
            }
        }
        if (a.chartConfig.tooltip != undefined) {//Configuration of tooltip
            //Without a text, this tooltip will not be created
            if (a.chartConfig.tooltip.text == undefined)
                a.chartConfig.tooltip = undefined;
            else {
                a.chartConfig.tooltip.name = a.chartConfig.name + "-toolTip";
                if (a.chartConfig.svg)
                    a.chartConfig.tooltip.parent = a.chartConfig.parent;
                else
                    a.chartConfig.tooltip.parent = "#" + a.chartConfig.name + "-container";
            }
        }
        a.chartConfig.interactions = d3.validEvents(a.chartConfig.interactions);//configuration pattern in JSUtil.js
        return this;
    }
    create() {//in this functions will be created all the components used in this chart.
        var a = this;
        this.dataSetter();//Configuration dataset to be used in this chart
        //Create a svg element if need
        this.svg = a.chartConfig.svg ?
            d3.select(a.chartConfig.parent) :
            d3.select(a.chartConfig.parent).append("svg").attr("id", a.chartConfig.name + "-container");

        if (!a.chartConfig.chart.calendar) {
            this.calendar.svg = a.chartConfig.calendar.svg && a.chartConfig.calendar.parent == undefined ?
                this.svg :
                (a.chartConfig.calendar.parent != undefined ?
                    d3.select(a.chartConfig.calendar.parent) :
                    d3.select(a.chartConfig.calendar.parent).append("svg").attr("id", a.chartConfig.name + "-calendar"));
            this.createChart(this.calendar, this.chartConfig.calendar);
        }
        if (!a.chartConfig.chart.hour) {
            this.hour.svg = a.chartConfig.hour.svg && a.chartConfig.hour.parent == undefined ?
                this.svg :
                (a.chartConfig.hour.parent != undefined ?
                    d3.select(a.chartConfig.hour.parent) :
                    d3.select(a.chartConfig.hour.parent).append("svg").attr("id", a.chartConfig.name + "-hour"));
            this.createChart(this.hour, this.chartConfig.hour);
            this.hour.collapse = this.hour.rectsContent.append("g").attr("id","collapse");
            this.hour.collapse.append("path");
            this.hour.collapse.append("rect").attr("opacity",0);
            this.hour.totalRects = this.hour.rectsContent.selectAll(".week").data(a.hour.totalData).enter()
                .append("g").attr("class", "week")
            this.hour.totalRects.append("rect");
            if (a.chartConfig.centerLabel != undefined)
                this.hour.totalRects.append("text").attr("class", "center").attr("text-anchor", "middle");
            if (a.chartConfig.cornerLabel != undefined)
                this.hour.totalRects.append("text").attr("class", "corner").attr("dy", "1.1em").attr("dx", "0.2em");
            
        }

        //Construct tooltip
        this.toolTipConstruct();

        return this;
    }
    createChart(chart, chartConfig) {
        chart.g = chart.svg.append("g");
        //create axis up (days of week)
        if (!chartConfig.axis.day.all)
            chart.dayAxis = chart.g.append("g");

        /*this is so that the whole region, including between squares, are valid for events*/

        chart.scrol = chart.g.append("g");//All the elements will be moved with scroll

        //create background
        chart.backscrol = chart.scrol.append("rect");
        //create axis left (weeks in dataset)
        if (!chartConfig.axis.vertical.all)
            chart.verticalAxis = chart.scrol.append("g");

        chart.rectsContent = chart.scrol.append("g").attr("id", "rects");
        //create rects to calendar chart
        chart.rects = chart.rectsContent.selectAll(".month").data(chart.data).enter()
            .append("g").attr("class", "month");
        chart.rects.append("rect");

        //Create texts
        if (chartConfig.texts.center != undefined)
            chart.rects.append("text").attr("class", "center").attr("text-anchor", "middle");
        if (chartConfig.texts.corner != undefined)
            chart.rects.append("text").attr("class", "corner").attr("dy", "1.1em").attr("dx", "0.2em");

        //Triangles to view scroll
        chart.extTriangles = chart.g.append("g");
        chart.extTriangles.append("path").attr("class", "up");
        chart.extTriangles.append("path").attr("class", "down");
    }
    draw() {
        var a = this;
        //Create the title
        this.titleConstruct();
        //copyParams
        this.width = a.chartConfig.dimensions.width;
        this.height = a.chartConfig.dimensions.height;
        this.calendar.margin = { top: 0, bottom: 0, left: 0, right: 0 };
        this.hour.margin = JSON.copyObject(a.calendar.margin);
        this.calendar.height = 0;
        this.hour.height = 0;

        if (!a.chartConfig.chart.calendar) {
            //create domain of weeks
            this.calendar.domain = a.weekDomain();
            this.calendar.margin = JSON.copyObject(a.chartConfig.calendar.margin);
            //re-size text based in width of text week's axis
            var temp = String.adjustWidth("00/XXX", a.chartConfig.layout.font_size, a.width * 0.1);
            this.font_size = Math.min(this.chartConfig.layout.font_size, temp);
        }
        if (!a.chartConfig.chart.hour) {
            this.hour.domain = a.weekDomain(this.chartConfig.hour.model);
            this.hour.margin = JSON.copyObject(a.chartConfig.hour.margin);
            //re-size text based in width of text hour's axis
            var temp = String.adjustWidth(a.chartConfig.hour.model == 4 ? "00h-00h" : "00XX", a.chartConfig.layout.font_size, a.width * 0.1);
            this.font_size = Math.min(this.chartConfig.layout.font_size, temp);
        }

        //Salva o antigo tamanho do titulo para reajuste
        var desloc = (a.chartConfig.title == undefined ? 0 : a.chartConfig.title.desloc);
        //resize calendar margin
        
        if (!a.chartConfig.chart.calendar) {
            this.calendar.margin.left = Math.max(a.calendar.margin.left, a.chartConfig.calendar.axis.vertical.all ? 0 :
                (11 + 3.00 * a.font_size));
            this.calendar.margin.top = Math.max(a.calendar.margin.top, (a.chartConfig.calendar.axis.day.all ? 20 :
                (11 + 1.05 * a.chartConfig.layout.font_size2)) + desloc);
            //height of chart
            this.calendar.height = a.chartConfig.calendar.extrapolation;
            if (a.calendar.domain.length < a.calendar.height)
                a.calendar.height = a.calendar.domain.length;
        }
        if (!a.chartConfig.chart.hour) {
            this.hour.margin.left = Math.max(a.hour.margin.left, a.chartConfig.hour.axis.vertical.all ? 0 :
                (11 + 3.00 * a.font_size));
            this.hour.margin.top = Math.max(a.hour.margin.top, a.chartConfig.hour.axis.day.all ? 20 :
                (11 + 1.05 * a.font_size + (a.chartConfig.chart.calendar ? desloc : 0)));
            this.hour.height = a.chartConfig.hour.extrapolation;
            if (a.chartConfig.hour.model < a.hour.height)
                a.hour.height = a.chartConfig.hour.model;
            this.hour.height++;
        }

        this.nVerticalRects = a.calendar.height + (a.calendar.height==0?a.hour.height:a.hour.height/1.5);
        this.size = a.chartConfig.dimensions.height - a.calendar.margin.top - a.calendar.margin.bottom
            - a.hour.margin.top - a.hour.margin.bottom;
        this.size = a.size / a.nVerticalRects;
        var tempSize = (a.chartConfig.dimensions.width - Math.max(a.calendar.margin.left, a.hour.margin.left)
            - Math.max(a.calendar.margin.right, a.hour.margin.right)) / 7;
        this.size = Math.min(this.size, tempSize);


        //create role of rects size
        /*this.size = Math.min(
            (a.chartConfig.dimensions.width - a.calendar.margin.left - a.calendar.margin.right) / 7
            ,
            (a.chartConfig.dimensions.height - a.calendar.margin.top - a.calendar.margin.bottom) /
            Math.min(a.calendar.domain.length, a.chartConfig.calendar.extrapolation)
        );*/



        //resize chart
        a.width = a.size * 7 + Math.max(a.calendar.margin.left, a.hour.margin.left)
            + Math.max(a.calendar.margin.right, a.hour.margin.right);
        a.height = a.size * this.nVerticalRects
            + a.calendar.margin.top + a.calendar.margin.bottom
            + a.hour.margin.top + a.hour.margin.bottom;
        //resize title
        this.titleConstruct();

        if (!a.chartConfig.chart.calendar) {
            //re-size text based in width of text week's axis
            var temp = String.adjustWidth("00/XXX", a.chartConfig.layout.font_size, a.calendar.margin.left*.8);
            this.font_size = Math.min(this.chartConfig.layout.font_size, temp);
        }
        if (!a.chartConfig.chart.hour) {
            //re-size text based in width of text hour's axis
            var temp = String.adjustWidth(a.chartConfig.hour.model == 4 ? "00h-00h" : "00XX", a.chartConfig.layout.font_size, a.hour.margin.left*.8);
            this.font_size = Math.min(this.chartConfig.layout.font_size, temp);
        }

        //resize top both margin
        if (!a.chartConfig.chart.calendar) {
            this.calendar.size = this.size;
            this.calendar.margin.top += -desloc +
                (a.chartConfig.title == undefined ? 0 : a.chartConfig.title.desloc);
            this.calendar.verticalFunction = MyDate.weekVal;
        }
        if (!a.chartConfig.chart.hour) {
            this.hour.size = this.size;
            var temp = 0;
            if (!a.chartConfig.chart.calendar) {
                this.hour.size/=1.5;
                temp += this.calendar.margin.top + this.calendar.margin.bottom + this.size * a.calendar.height;
            }
            this.hour.margin.top += -(a.chartConfig.chart.calendar ?
                (desloc - (a.chartConfig.title == undefined ? 0 : a.chartConfig.title.desloc)) : 0) + temp;
            this.hour.verticalFunction = MyDate.dayVal;
        }


        //create formula horizontal of axis
        this.day = d3.scaleBand().rangeRound([0, 7 * a.size]).domain(MyDate.weekName()).padding(a.chartConfig.layout.padding);
        //radius of rect's corner
        this.rCorner = this.day.bandwidth() * a.chartConfig.layout.corner / 2;

        if (!a.chartConfig.chart.calendar) {
            this.drawChart(a.calendar, a.chartConfig.calendar);
        }
        if (!a.chartConfig.chart.hour) {
            this.drawChart(a.hour, a.chartConfig.hour);
            
            var translatebefore = a.hour.g.attr("transform").replace("translate(", "").replace(")", "").split(",");
            a.hour.g.attr("transform", "translate(" + translatebefore[0] + "," + (parseFloat(translatebefore[1]) + a.size) + ")");
            if (!a.chartConfig.hour.axis.day.all)
                a.hour.dayAxis.attr("transform", "translate(0," + (-a.size) + ")");

            var max = d3.max(a.hour.totalData, function (d) {
                return d.value;
            });
            var min = d3.min(a.hour.totalData, function (d) {
                return d.value;
            });
            var den = (max - min);
            var color = function (value) {
                return value == 0 ? 0 : (0.1 + (value - min) / den);
            }
            //.colors(color(d.value));

            this.hour.totalRects
                //.transition().delay(200).transition(0)
                .attr("fill", function (d) { return (d.value - min) / den > 0.8 ? "#fff" : "#000"; })
                .attr("transform", function (d, i) {
                    return "translate(" + a.day(MyDate.weekName()[i]) + "," + (a.hour.vertical(a.hour.vertical.domain()[0]) - a.size) + ")";
                });
            this.hour.totalRects.select("rect")
                //.transition().delay(200).transition(0)
                .attr("rx", a.rCorner).attr("ry", a.rCorner)
                .attr("width", a.day.bandwidth())
                .attr("height", a.day.bandwidth())
                .attr("fill", function (d) {
                    return a.chartConfig.layout.colors(color(d.value)+0.1);
                });
            if (a.chartConfig.hour.texts.corner != undefined)
                this.hour.totalRects.select(".corner")
                    //.transition().delay(200).transition(0)
                    .attr("font-size", a.font_size * .5)
                    .text(function (d, i) {
                        return d3.textData(d, a.chartConfig.hour.texts.center);
                    });

            if (a.chartConfig.hour.texts.center != undefined)
                this.hour.totalRects.select(".center")
                    //.transition().delay(200).transition(0)
                    .attr("font-size", a.font_size * .9)
                    .attr("dy", a.font_size * .20 + a.hour.vertical.bandwidth() / 2)
                    .attr("dx", a.hour.vertical.bandwidth() / 2)
                    .text(function (d, i) {
                        return String.adjustLength(d3.textData(d, a.chartConfig.hour.texts.center),
                            a.font_size * .9, a.hour.vertical.bandwidth(), true);
                    });

            a.hour.hourShow = true;
            var temp= a.hour.vertical(a.hour.domain[0]);
            a.hour.collapse.attr("transform","translate("+(-a.size)+","+(-a.size+temp/2)+")")
                .on("mouseover",function(d){ d3.select(this).select("path").attr("stroke-width", 2); })
                .on("mouseout",function(d){ d3.select(this).select("path").attr("stroke-width", 0); })
                .on("click",function(d){
                    a.hourView();
                }).select("rect").attr("width",a.size*8).attr("height",a.size);


            this.hourView();

        }

        //Functions of key press
        d3.select("body").on("keydown", function (event) {
            if (a.calendar.on) {
                if (d3.event.keyCode == 38) {//up Arrow
                    if(a.scrolMove(a.calendar.scrolposition - 1, a.calendar, a.chartConfig.calendar))
                        d3.event.preventDefault();
                } else if (d3.event.keyCode == 40) {//down Arrow
                    if(a.scrolMove(a.calendar.scrolposition + 1, a.calendar, a.chartConfig.calendar))
                        d3.event.preventDefault();
                } else if ((d3.event.keyCode == 34 || d3.event.keyCode == 32)) {//page Down || space
                    if(a.scrolMove(a.calendar.scrolposition + a.chartConfig.calendar.extrapolation, a.calendar, a.chartConfig.calendar))
                        d3.event.preventDefault();
                } else if (d3.event.keyCode == 33) {//page up
                    if(a.scrolMove(a.calendar.scrolposition - a.chartConfig.calendar.extrapolation, a.calendar, a.chartConfig.calendar))
                        d3.event.preventDefault();
                } else if (d3.event.keyCode == 35) {//end
                    if(a.scrolMove(a.calendar.scrolMax, a.calendar, a.chartConfig.calendar))
                        d3.event.preventDefault();
                } else if (d3.event.keyCode == 36) {//home
                    if(a.scrolMove(0, a.calendar, a.chartConfig.calendar))
                        d3.event.preventDefault();
                }
            }
            if (a.hour.on) {
                if (d3.event.keyCode == 38) {//up Arrow
                    if(a.scrolMove(a.hour.scrolposition - 1, a.hour, a.chartConfig.hour))
                        d3.event.preventDefault();
                } else if (d3.event.keyCode == 40) {//down Arrow
                    if(a.scrolMove(a.hour.scrolposition + 1, a.hour, a.chartConfig.hour))
                        d3.event.preventDefault();
                    
                } else if ((d3.event.keyCode == 34 || d3.event.keyCode == 32)) {//page Down || space
                    if(a.scrolMove(a.hour.scrolposition + a.chartConfig.hour.extrapolation, a.hour, a.chartConfig.hour))
                        d3.event.preventDefault();
                } else if (d3.event.keyCode == 33) {//page up
                    if(a.scrolMove(a.hour.scrolposition - a.chartConfig.hour.extrapolation, a.hour, a.chartConfig.hour))
                        d3.event.preventDefault();
                } else if (d3.event.keyCode == 35) {//end
                    if(a.scrolMove(a.hour.scrolMax, a.hour, a.chartConfig.hour))
                        d3.event.preventDefault();
                } else if (d3.event.keyCode == 36) {//home
                    if(a.scrolMove(0, a.hour, a.chartConfig.hour))
                        d3.event.preventDefault();
                }
            }

        });

        return this;
    }
    drawChart(chart, chartConfig) {
        var a = this;
        //draw background's rect 
        chart.backscrol.attr("fill", "#fff").attr("width", this.size * 7).attr("height", this.size * chart.height);

        //create formula vertical of axis
        chart.verticalRange = [0, chart.domain.length * chart.size];
        chart.vertical = d3.scaleBand().rangeRound(chart.verticalRange).domain(chart.domain).padding(a.chartConfig.layout.padding);
        chart.size2 = chart.vertical(chart.vertical.domain()[1]) - chart.vertical(chart.vertical.domain()[0]);

        //max value to range scale
        var max = d3.max(chart.data, function (d) {
            return d.value;
        });
        var min = d3.min(chart.data, function (d) {
            return d.value;
        });
        var den = (max - min);
        var color = function (value) {
            return value == 0 ? 0 : (0.1 + (value - min) / den);
        }
        //.colors(color(d.value));



        //hide all rects
        chart.rects.transition().duration(200).attr("opacity", 0);

        //Set svg and global group
        if (!this.chartConfig.svg)
            chart.svg.attr("width", a.width).attr("height", a.height);
        chart.g.attr("transform", "translate(" + chart.margin.left + "," + chart.margin.top + ")");

        //Set Weeks Axis
        if (!chartConfig.axis.vertical.all) {
            chart.verticalAxis.transition().transition(500).call(d3.axisLeft(chart.vertical)).attr("font-size", a.font_size);
            if (!chartConfig.axis.vertical.lines) {
                chart.verticalAxis.selectAll("line").transition().remove();
                chart.verticalAxis.select("path").transition().remove();
            }
        }

        //Set Days of Week Axis
        if (!chartConfig.axis.day.all) {
            chart.dayAxis.transition().transition(500).call(d3.axisTop(a.day)).attr("font-size", a.chartConfig.layout.font_size2);
            chart.dayAxis.selectAll("text").transition().text(function (d, i) {
                return String.adjustLength(MyDate.weekName()[i], a.chartConfig.layout.font_size2, chart.vertical.bandwidth());
            });
            if (!chartConfig.axis.day.lines) {
                chart.dayAxis.selectAll("line").transition().remove();
                chart.dayAxis.select("path").transition().remove();
            }
        }

        //Set rect's group of CalendarHeatMap
        chart.rects
            //.transition().delay(200).transition(0)
            .attr("transform", function (d, i) {
                return "translate(" + a.day(MyDate.weekName()[d.dayOfWeek]) + "," + chart.vertical(chart.verticalFunction(chart.domain, d)) + ")";
            });

        //Set rect in rect's group
        chart.rects.attr("fill", function (d) { return (d.value - min) / den > 0.8 ? "#fff" : "#000"; }).select("rect")
            //.transition().delay(200).transition(0)
            .attr("rx", a.rCorner).attr("ry", a.rCorner)
            .attr("width", a.day.bandwidth())
            .attr("height", chart.vertical.bandwidth())
            .attr("fill", function (d) {

                return chartConfig.colors(color(d.value)+0.1);
            });

        //set corner Label
        if (a.chartConfig.cornerLabel != undefined)
            chart.rects.select(".corner")
                //.transition().delay(200).transition(0)
                .attr("font-size", a.font_size * .5)
                .text(function (d, i) {
                    return d3.textData(d, a.chartConfig.cornerLabel.text);
                });

        //set center Label
        if (a.chartConfig.centerLabel != undefined)
            chart.rects.select(".center")
                //.transition().delay(200).transition(0)
                .attr("font-size", a.font_size * .9)
                .attr("dy", a.font_size * .3 + chart.vertical.bandwidth() / 2)
                .attr("dx", chart.vertical.bandwidth() / 2)
                .text(function (d, i) {
                    return String.adjustLength(d3.textData(d, a.chartConfig.centerLabel.text),
                        a.font_size * .9, chart.vertical.bandwidth(), true);
                });

        //If is necessary create a scrol function
        if (chart.domain.length > chartConfig.extrapolation) {
            //Actvate scrol
            chart.extrapolation = true;
            //Location of comparation
            var location = chartConfig.extrapolation * chart.size2;// -chart.vertical.bandwidth();
            var location2 = (chartConfig.extrapolation + 1) * chart.size;// +2*chart.vertical.bandwidth();

            //Set view Rects
            chart.rects.transition().delay(500).duration(500).attr("opacity", function (d) {
                if (chart.vertical(chart.verticalFunction(chart.domain, d)) > location)
                    return 0;
                else
                    return 1;
            }).attr("transform", function (d) {
                var temp = chart.vertical(chart.verticalFunction(chart.domain, d));
                if (temp > location2 || temp < -2 * chart.vertical.bandwidth())
                    return "translate(" + -3 * a.day.bandwidth() + "," + chart.vertical(chart.verticalFunction(chart.domain, d)) + ")";
                else
                    return "translate(" + a.day(MyDate.weekName()[d.dayOfWeek]) + "," + chart.vertical(chart.verticalFunction(chart.domain, d)) + ")";
            });

            //Set Weeks' axis
            if (!chartConfig.axis.vertical.all) {

                chart.verticalsTiks = chart.verticalAxis.selectAll(".tick");

                chart.verticalsTiks.transition().delay(500).duration(500).attr("opacity", function (d) {
                    if (chart.vertical(chart.verticalFunction(chart.domain, d)) > location) {
                        return 0;
                    } else
                        return 1;
                }).attr("transform", function (d) {
                    var temp = chart.vertical(chart.verticalFunction(chart.domain, d));
                    if (temp > location2 || temp < -2 * chart.vertical.bandwidth())
                        return "translate(" + -2 * a.day.bandwidth() + "," + (chart.vertical(chart.verticalFunction(chart.domain, d)) + chart.vertical.bandwidth() / 2) + ")";
                    else return "translate(" + 0 + "," + (chart.vertical(chart.verticalFunction(chart.domain, d)) + chart.vertical.bandwidth() / 2) + ")";
                });
            }
            this.scrolEvents(chart, chartConfig);



        } else {
            //if no extrapolation, only show all rects
            chart.rects.transition().delay(500).duration(500).attr("opacity", 1);
        }
    }
    scrolEvents(chart, chartConfig) {
        var a = this;
        //Set Triangles of scrol

        //move scroll's triangles
        chart.extTriangles.attr("transform", "translate(" + -chart.margin.left / 2 + "," + chart.vertical(chart.vertical.domain()[0]) + ")");

        var y = chart.vertical(chart.domain[0])+chartConfig.extrapolation*chart.size2 - .25 * chart.size2;
        var yu = chart.vertical(chart.vertical.domain()[0]) - chart.size2 * .25;
        var seta = function (position) {
            var ret = [];
            if (position == 1)
                ret = [{ "x": 0, "y": y + .25 * chart.size2 },
                { "x": -a.size / 3, "y": y },
                { "x": a.size / 3, "y": y }];
            else
                ret = [{ "x": 0, "y": yu - .25 * chart.size2 },
                { "x": -a.size / 3, "y": yu },
                { "x": a.size / 3, "y": yu }];

            return ret;
        }

        var lineFunction = d3.line()
            .x(function (d) { return d.x; }) // set the x values for the line
            // generator
            .y(function (d) { return d.y; }) // set the y values for the line
            // generator
            .curve(d3.curveLinearClosed);
        chart.extTriangles.select(".up").attr("opacity", 0)
            .attr("d", lineFunction(seta(0)))
            .attr("stroke", chartConfig.colors(0.5))
            .attr("stroke-width", 2)
            .attr("fill", chartConfig.colors(0.5));
        

        chart.extTriangles.select(".down").attr("opacity", 0)
            .attr("d", lineFunction(seta(1)))
            .attr("stroke", chartConfig.colors(0.5))
            .attr("stroke-width", 2)
            .attr("fill", chartConfig.colors(0.5));
        chart.extTriangles.select(".down").transition().duration(500).attr("opacity", 1);

        //Configures events to scrol
        chart.scrolposition = 0;//scroll index
        chart.scrolMax = chart.domain.length - chartConfig.extrapolation;//scroll range

        //function to action with "zoom"(wheel of mouse)
        var build = function (d) {
            if (d3.event.sourceEvent == undefined || d3.event.sourceEvent.deltaY == undefined)
                return;
            var param = d3.event.sourceEvent.deltaY>0?1:-1;

            a.scrolMove(chart.scrolposition + param, chart, chartConfig);
        }
        var zoom = d3.zoom()
            .on("zoom", build);
        chart.scrol.call(zoom);

        //function to actions with keyboard press
        //ONLY WORKS if mouse be over region of chart
        chart.on = false;
        chart.g.on("mouseover", function (d) {
            chart.on = true;
        });
        chart.g.on("mouseout", function (d) {
            chart.on = false;
        });

        //Function to scrol with click on triangles
        chart.extTriangles.selectAll("path").on("click", function (d) {
            var element = d3.select(this);
            if (element.attr("class") == "up")
                a.scrolMove(chart.scrolposition - 1, chart, chartConfig);
            else if (element.attr("class") == "down")
                a.scrolMove(chart.scrolposition + 1, chart, chartConfig);
        });
    }
    scrolMove(position, chart, chartConfig) {
        var a = this;
        if (chart.extrapolation) {//Do only if exists extrapolation
            if (chart.scrolposition == position) {
                return false;//Not Do if already in position
            }
            chart.scrolposition = position;
            chart.scrolposition = chart.scrolposition > (chart.scrolMax) ? (chart.scrolMax) : chart.scrolposition;//Only move until max
            chart.scrolposition = chart.scrolposition < 0 ? 0 : chart.scrolposition;//Only move until min

            var location = chartConfig.extrapolation * chart.size2;// -chart.vertical.bandwidth();
            var location2 = (chartConfig.extrapolation + 1) * chart.size;// +2*chart.vertical.bandwidth();

            chart.extTriangles.select(".up").attr("opacity", (chart.scrolposition == 0 ? 0 : 1));//Shou up's triangle
            chart.extTriangles.select(".down").attr("opacity", (chart.scrolposition == chart.scrolMax ? 0 : 1));//Shou down's triangle

            chart.rects.attr("transform", function (d) {
                return "translate(" + a.day(MyDate.weekName()[d.dayOfWeek]) + "," + chart.vertical(chart.verticalFunction(chart.domain, d)) + ")";
            });
            if (!chartConfig.axis.vertical.all)
                chart.verticalAxis.selectAll(".tick").attr("transform", function (d) {
                    var temp = chart.vertical(chart.verticalFunction(chart.domain, d));
                    if (temp > location2 || temp < -2 * chart.vertical.bandwidth())
                        return "translate(" + -2 * a.day.bandwidth() + "," + (chart.vertical(chart.verticalFunction(chart.domain, d)) + chart.vertical.bandwidth() / 2) + ")";
                    else return "translate(" + 0 + "," + (chart.vertical(chart.verticalFunction(chart.domain, d)) + chart.vertical.bandwidth() / 2) + ")";
                });

            chart.vertical.rangeRound(chart.verticalRange.map(function (d) { return d - chart.scrolposition * chart.size2; }));//move weeks axis



            if (!chartConfig.axis.vertical.all) {//Set Weeks axis
                chart.verticalAxis
                    .transition().duration(500)
                    .call(d3.axisLeft(chart.vertical)).attr("font-size", a.font_size)
                    .selectAll(".tick").attr("opacity", function (d) {
                        var temp = chart.vertical(chart.verticalFunction(chart.domain, d));
                        if (temp > location || temp < 0) return 0;
                        else return 1;
                    }).attr("transform", function (d) {
                        var temp = chart.vertical(chart.verticalFunction(chart.domain, d));
                        if (temp > location2 || temp < -2 * chart.vertical.bandwidth())
                            return "translate(" + -2 * a.day.bandwidth() + "," + (chart.vertical(chart.verticalFunction(chart.domain, d)) + chart.vertical.bandwidth() / 2) + ")";
                        else return "translate(" + 0 + "," + (chart.vertical(chart.verticalFunction(chart.domain, d)) + chart.vertical.bandwidth() / 2) + ")";
                    });
                if (!chartConfig.axis.vertical.lines) {
                    chart.verticalAxis.selectAll("line").remove();
                    chart.verticalAxis.select("path").remove();
                }
            }

            chart.rects//Set Rects to Show
                .transition().duration(500)
                .attr("transform", function (d, i) {
                    return "translate(" + a.day(MyDate.weekName()[d.dayOfWeek]) + "," + chart.vertical(chart.verticalFunction(chart.domain, d)) + ")";
                }).attr("opacity", function (d) {
                    var temp = chart.vertical(chart.verticalFunction(chart.domain, d));
                    if (temp > location || temp < 0) {
                        return 0;
                    } else
                        return 1;
                });

            chart.rects.transition().delay(550).attr("transform", function (d) {
                var temp = chart.vertical(chart.verticalFunction(chart.domain, d));
                if (temp > location2 || temp < -2 * chart.vertical.bandwidth())
                    return "translate(" + -3 * a.day.bandwidth() + "," + chart.vertical(chart.verticalFunction(chart.domain, d)) + ")";
                else
                    return "translate(" + a.day(MyDate.weekName()[d.dayOfWeek]) + "," + chart.vertical(chart.verticalFunction(chart.domain, d)) + ")";
            });
            return true;
        }
        return false;
    }
    hourView(){
        var a = this;
        if(!a.chartConfig.chart.hour){
            var icon = function (position) {
                var ret = [];
                if (position)
                    ret = d3.path.icons.arrow_down(a.size*.4);
                else
                    ret = ret = d3.path.icons.arrow_right(a.size*.4);
                return ret;
            }
            var lineFunction = d3.path.lineFunction(d3.curveLinearClosed);
            if(a.hour.hourShow){
                //a.hour.scrolposition = 0;
                a.hour.rects.transition().delay(0).duration(500)
                    .attr("transform",function(d){
                        return "translate("+a.day(MyDate.weekName()[d.dayOfWeek])+","+(a.hour.vertical(a.hour.vertical.domain()[(a.hour.scrolposition?a.hour.scrolposition:0)])-a.hour.size2)+")"
                    }).attr("opacity",0);
                //console.log((a.hour.vertical(a.hour.vertical.domain()[0])-a.hour.size2));
                if(!a.chartConfig.hour.axis.vertical.all)
                    a.hour.verticalAxis.selectAll(".tick").transition().delay(0).duration(500)
                        .attr("transform",function(d){
                            return "translate("+0+","+(a.hour.vertical(a.hour.vertical.domain()[(a.hour.scrolposition?a.hour.scrolposition:0)])-a.hour.size2/2)+")";
                        }).attr("opacity",0);
                if(a.hour.extrapolation)
                    a.hour.extTriangles.selectAll("path").transition().delay(0).duration(500).attr("opacity",0);
            }else{
                var location = a.chartConfig.hour.extrapolation * a.hour.size2;// -a.hour.vertical.bandwidth();
                var location2 = (a.chartConfig.hour.extrapolation + 1) * a.hour.size;// +2*a.hour.vertical.bandwidth();
                a.hour.rects
                    .transition().transition(500)
                    .attr("transform", function (d, i) {
                        return "translate(" + a.day(MyDate.weekName()[d.dayOfWeek]) + "," + a.hour.vertical(a.hour.verticalFunction(a.hour.domain, d)) + ")";
                    }).attr("opacity", function (d) {
                        var temp = a.hour.vertical(a.hour.verticalFunction(a.hour.domain, d));
                        if (temp > location || temp < 0) {
                            return 0;
                        } else
                            return 1;
                    });
                if (!a.chartConfig.hour.axis.vertical.all) {//Set Weeks axis
                    a.hour.verticalAxis
                        .selectAll(".tick").transition().duration(500).attr("opacity", function (d) {
                            var temp = a.hour.vertical(a.hour.verticalFunction(a.hour.domain, d));
                            if (temp > location || temp < 0) return 0;
                            else return 1;
                        }).attr("transform", function (d) {
                            var temp = a.hour.vertical(a.hour.verticalFunction(a.hour.domain, d));
                            if (temp > location2 || temp < -2 * a.hour.vertical.bandwidth())
                                return "translate(" + -2 * a.day.bandwidth() + "," + (a.hour.vertical(a.hour.verticalFunction(a.hour.domain, d)) + a.hour.vertical.bandwidth() / 2) + ")";
                            else return "translate(" + 0 + "," + (a.hour.vertical(a.hour.verticalFunction(a.hour.domain, d)) + a.hour.vertical.bandwidth() / 2) + ")";
                        });
                }
                if(a.hour.extrapolation){
                    a.hour.extTriangles.select(".down").attr("opacity", (a.hour.scrolposition == a.hour.scrolMax ? 0 : 1));//Shou down's triangle
                }
            }
            a.hour.hourShow = !a.hour.hourShow;
            a.hour.collapse
                .select("path").transition().duration(500)
                    .attr("d", lineFunction(icon(a.hour.hourShow)))
                    .attr("transform","translate("+(a.day(a.day.domain()[0])+a.day.bandwidth()*.5)+","+(a.size*.3)+")")
                    .attr("stroke", a.chartConfig.hour.colors(0.5))
                    .attr("stroke-width", 0)
                    .attr("fill", a.chartConfig.layout.colors(0.8));
        }
    }
    dataSetter() {//Configurations of dataset
        var a = this;
        a.data = a.chartConfig.data;
        a.data = a.data.map(function (d) {//Make shure of a Pattern
            /*var temp = new MyDate($(d).attr(a.chartConfig.dataConfig.year),
                $(d).attr(a.chartConfig.dataConfig.month),
                $(d).attr(a.chartConfig.dataConfig.day),
                $(d).attr(a.chartConfig.dataConfig.hour),
                $(d).attr(a.chartConfig.dataConfig.value));
            temp.dayOfWeek = MyDate.dayOfWeek(temp);
            return temp;*/
            d.year = $(d).attr(a.chartConfig.dataConfig.year);
            d.month = $(d).attr(a.chartConfig.dataConfig.month);
            d.day = $(d).attr(a.chartConfig.dataConfig.day);
            d.hour = $(d).attr(a.chartConfig.dataConfig.hour);
            d.value = $(d).attr(a.chartConfig.dataConfig.value);
            d.dayOfWeek = MyDate.dayOfWeek(d);
            return d;/**/
        });
        
       /* this.chartConfig.data = a.data.filter(function (d) {//Filter (only to data generic generate)
            var nDay = MyDate.nDays(d);
            return d.day <= nDay;
        });*/

        
        
        this.chartConfig.data = a.data.sort(MyDate.greatThan);//Order by dataTime of less to greater
        //Do only if hour was solicited
        if (!a.chartConfig.chart.hour) {
            a.hour.totalData = [];
            for (var i = 0; i < 7; i++) {
                a.hour.totalData[i] = {};
                a.hour.totalData[i].value = 0;
                a.hour.totalData[i].dayOfWeek = i;
                this.hour.totalData[i].toString = function () {
                    return MyDate.weekName(this.dayOfWeek);
                }
            }
            this.hour.data = [];
            var model = (a.chartConfig.hour.model == 4 ? 4 : 24);
            for (var i = 0; i < 7 * model; i++) {
                this.hour.data[i] = {};
                this.hour.data[i].value = 0;
                this.hour.data[i].dayOfWeek = parseInt(i / model);
                if (model == 4){
                    this.hour.data[i].hour = (i % 4) * 6;
                    this.hour.data[i].hour = (this.hour.data[i].hour<10?"0":"")+this.hour.data[i].hour+"h-"+((this.hour.data[i].hour+6)<10?"0":"")+(this.hour.data[i].hour+6)+"h"
                }else this.hour.data[i].hour = (i % model);
                this.hour.data[i].toString = function () {
                    return "" + MyDate.weekName(this.dayOfWeek) + "," + MyDate.dayVal(MyDate.hourNames(undefined, model), this);
                }
            }
            for (var i = 0; i < a.data.length; i++) {
                a.hour.totalData[a.data[i].dayOfWeek].value += a.data[i].value;
                if (a.chartConfig.hour.model == 4) {
                    if(a.data[i].hour>=24)
                    console.log(a.data[i].hour);
                    //console.log(a.data[i].dayOfWeek * 4 + Math.floor(a.data[i].hour / 6));
                    this.hour.data[a.data[i].dayOfWeek * 4 + parseInt(a.data[i].hour / 6)].value += a.data[i].value;
                } else
                    this.hour.data[a.data[i].dayOfWeek * 24 + a.data[i].hour].value += a.data[i].value;
            }
        }
        //Do only if calendar was solicited
        if (!a.chartConfig.chart.calendar) {
            //Interval of time to chart 
            //This is like a valid data, but only here the data can be used(filtered and ordened)
            if (a.chartConfig.dataConfig.init == undefined) a.chartConfig.dataConfig.init = {};
            if (a.chartConfig.dataConfig.init.year == undefined) a.chartConfig.dataConfig.init.year = a.data[0].year;
            if (a.chartConfig.dataConfig.init.month == undefined) a.chartConfig.dataConfig.init.month = a.data[0].month;
            if (a.chartConfig.dataConfig.init.day == undefined) a.chartConfig.dataConfig.init.day = a.data[0].day;
            

            if (a.chartConfig.dataConfig.end == undefined) a.chartConfig.dataConfig.end = {};
            if (a.chartConfig.dataConfig.end.year == undefined) a.chartConfig.dataConfig.end.year =
                a.data[a.data.length - 1].year;
            if (a.chartConfig.dataConfig.end.month == undefined) a.chartConfig.dataConfig.end.month =
                a.data[a.data.length - 1].month;
            if (a.chartConfig.dataConfig.end.day == undefined) a.chartConfig.dataConfig.end.day =
                a.data[a.data.length - 1].day;
            

            a.chartConfig.dataConfig.init = new MyDate(a.chartConfig.dataConfig.init.year,
                a.chartConfig.dataConfig.init.month,
                a.chartConfig.dataConfig.init.day);
            a.chartConfig.dataConfig.end = new MyDate(a.chartConfig.dataConfig.end.year,
                a.chartConfig.dataConfig.end.month,
                a.chartConfig.dataConfig.end.day);
            
            this.calendar.data = [];//The data will be transferr to here. Already sum and filled;
            // This is to calculate all the days between the init and end of dataset
            var start = a.chartConfig.dataConfig.init;
            var end = a.chartConfig.dataConfig.end;

            var years = end.year - start.year + 1;
            var months = 12 * (years - 1) + end.month - start.month + 1;
            var j = new MyDate(0, 0, 0, 0, 0);
            var offset = new MyDate(0, 1, 0, 0, 0);
            var days = [];
            var indexData = 0;
            //go through months
            for (var i = 0, j = MyDate.sum(j, start); i < months; i++ , j = MyDate.sum(j, offset)) {
                // this save ndays on vector to get all the days in dataset to calendar
                if (i == 0) {
                    days[i] = MyDate.nDays(j) - start.day + 1;
                } else if (i == months - 1) {
                    days[i] = end.day;
                } else {
                    days[i] = MyDate.nDays(j);
                }
                var offset = new MyDate(0, 0, 1, 0, 0);
                var k = 0;
                //go through days of month
                for (j.day = 1, j.value = 0; k < days[i]; k++ , j = MyDate.sum(j, offset)) {
                    j.dayOfWeek = MyDate.dayOfWeek(j);
                    //sum values of this day(in all of hours)
                    while (a.data[indexData] && MyDate.greatThan(a.data[indexData], j, true) == 0) {
                        j.value += a.data[indexData].value;
                        indexData++;
                    }
                    //Add reg to data set calendar
                    this.calendar.data.push(new MyDate(j.year,
                        j.month,
                        j.day,
                        undefined,
                        j.value,
                        j.dayOfWeek)
                    );
                    //console.log(this.calendar.data[this.calendar.data.length-1])
                }
            }
            //console.log(a.chartConfig.dataConfig.end.month);
            //console.log(a.calendar.data);
        }
        return this;
    }
    resize(width, height) {//Redimensions of chart
        if (width != undefined)
            this.chartConfig.dimensions.width = width;
        if (height != undefined)
            this.chartConfig.dimensions.height = height;
        var a = this;

        return this.draw();
    }
    weekDomain(model) {//return the domain of weeks
        switch (model) {
            case 4: case 12: case 24:
                return MyDate.hourNames(undefined, model);
            default:
                var a = this;

                var start = a.calendar.data[0];
                var end = a.calendar.data[a.calendar.data.length - 1];
                var domain = [new MyDate(start.year, start.month, start.day - start.dayOfWeek)];

                while (MyDate.greatThan(domain[domain.length - 1], end) == -1) {
                    domain.push(MyDate.sum(domain[domain.length - 1], { day: 7 }));
                }
                domain.pop();
                return domain;
        }
    }
    titleConstruct() {//construct Title
        var a = this;
        var b = JSON.copyObject(a.chartConfig.dataConfig);
        b.init.month = MyDate.monthName(b.init.month);
        b.end.month = MyDate.monthName(b.end.month);
        if (a.chartConfig.title != undefined) {
            if (this.titleElement == undefined)
                this.titleElement = this.svg.append("text")
                    .attr("id", "titleElement_" + this.chartConfig.name)
                    .style("font-size", a.chartConfig.title.font.size)
                    .style("font-family", a.chartConfig.title.font.name)
                    .attr("fill", "#FFF")
                    .text(function () {
                        return d3.textData(a.chartConfig.dataConfig, a.chartConfig.title.text);
                    }).attr("fill", a.chartConfig.title.color.text);

            this.titleElement
                .style("font-size", String.adjustWidth(this.titleElement.text(), a.chartConfig.title.font.size, a.width));

            a.chartConfig.title.position.dy = parseInt(this.titleElement.style("font-size").replace("px", "")) / 3;
            var labelDim = document.getDimensions("#titleElement_" + this.chartConfig.name);
            this.titleElement
                .attr("transform", function () {
                    if (a.chartConfig.title.position.align == "middle")
                        return "translate(" + (a.width / 2 - labelDim.w / 2) + ", " + 2 * labelDim.h / 3 + " )";
                    else if (a.chartConfig.title.position.align == "end")
                        return "translate(" + (a.width - labelDim.w) + ", " + 2 * labelDim.h / 3 + " )";
                    else
                        return "translate(" + 4 + ", " + 2 * labelDim.h / 3 + " )";
                });
            var titleD = document.getDimensions("#titleElement_" + this.chartConfig.name);
            a.chartConfig.title.desloc = titleD.h;

        }
        return this;
    }
    toolTipConstruct() {//Construct and configurate toltip
        var a = this;
        if (this.chartConfig.tooltip != undefined) {
            this.toolTip = new ToolTip(this.chartConfig.tooltip);
            a.chartConfig.interactions.mouseover.push(function (element, data) {
                element = d3.select(element);
                if (element.attr("opacity") != 0)
                    a.toolTip.show(data);
            });
            a.chartConfig.interactions.mousemove.push(function (element, data) {
                a.toolTip.move();
            });
            a.chartConfig.interactions.mouseout.push(function (element, data) {
                a.toolTip.hide();
            });
        }
        return this;
    }
    addInteractions() {
        var a = this;
        a.chartConfig.interactions.mouseover.push(function (element, data) {
            var currentEl = d3.select(element).select("rect");
            currentEl.attr("opacity", 0.8);
            currentEl.attr('stroke-width', '3').attr("stroke", a.chartConfig.layout.colors(0.5));
        });
        a.chartConfig.interactions.mouseout.push(function (element, data) {
            var currentEl = d3.select(element).select("rect");
            currentEl.attr("opacity", 1);
            currentEl.attr('stroke-width', '0').attr("stroke", a.chartConfig.layout.colors(0));
        });

        d3.addEvents(a.calendar.rects, a.chartConfig.interactions);
        d3.addEvents(a.hour.rects, a.chartConfig.interactions);
        d3.addEvents(a.hour.totalRects, a.chartConfig.interactions);

        return this;
    }
}