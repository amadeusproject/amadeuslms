var ganttCont = 0;
var temp, temp2;
class GanttChart {
    constructor(chartConfig) {
        this.create(GanttChart.validData(chartConfig)).draw();
    }
    static validData(chartConfig) {
        if (chartConfig.data == undefined) {
            console.error("Without Dataset");
            throw new Exeption();
        }

        if (chartConfig.name == undefined) chartConfig.name = "GanttChart" + (ganttCont++);
        if (chartConfig.parent == undefined) chartConfig.parent = "body";
        GanttChart.definewidth(chartConfig);
        if (chartConfig.margin == undefined) chartConfig.margin = {};
        if (chartConfig.margin.top == undefined) chartConfig.margin.top = 20;
        if (chartConfig.margin.right == undefined) chartConfig.margin.right = 10;
        if (chartConfig.margin.bottom == undefined) chartConfig.margin.bottom = 30;
        if (chartConfig.margin.left == undefined) chartConfig.margin.left = 10;

        if (chartConfig.layout == undefined) chartConfig.layout = {};
        if (chartConfig.layout.maxrow == undefined) chartConfig.layout.maxrow = 5;
        if (chartConfig.layout.contextHeight == undefined) chartConfig.layout.contextHeight = 0.1;
        if (chartConfig.layout.colors == undefined || chartConfig.layout.colors.length != 5)
            chartConfig.layout.colors = ["#AD1111", "#FAA916", "#0B4F6C", "#343434", "#00993F"]
        //0-atrasado 1-dentro_do_prazo 2-pendencia futura 3-não_concluida 4-finalizada
        //if (chartConfig.layout.backcolors == undefined || chartConfig.layout.backcolors.length != 5)
        //  chartConfig.layout.backcolors = ["#C43535", "#F9BA43", "#218AB7", "#545454", "#00C150"];
        //0-atrasado 1-dentro_do_prazo 2-pendencia futura 3-não_concluida 4-finalizada
        if (chartConfig.layout.texts == undefined || chartConfig.layout.texts.length != 5)
            chartConfig.layout.texts = ["Atrasada", "Dentro do Prazo", "Pendência Futura", "Perdida", "Concluída"];
        if (chartConfig.layout.texts2 == undefined || chartConfig.layout.texts2.length != 5)
            chartConfig.layout.texts2 = ["Esta tarefa está atrasada", "Você ainda não realizou esta tarefa", "", "Você perdeu esta tarefa", ""];
        if (chartConfig.layout.min_size_card == undefined) chartConfig.layout.min_size_card = 200;

        chartConfig.now = new Date();
        var now = chartConfig.now.getTime();

        var positions = [];
        for (var i = 0; i < chartConfig.layout.maxrow; i++)
            positions.push(null);

        function type(d, i) {
            //Validação linha a linha
            if (d == undefined)
                return
            if (d.date == undefined ||
                d.date.start == undefined ||
                d.date.end == undefined ||
                d.name == undefined) {
                console.error("invalid row of dataSet \"" + i + "\" ");
                throw new Exception();
            }
            if (d.percent == undefined) d.percent = 0;
            d.percent = +d.percent;
            if (d.percent > 1) d.percent = 1;
            if (d.percent < 0) d.percent = 0;
            //Configurando datas
            if (d.date.start != undefined) {
                d.date.start = new Date(d.date.start);
            }

            if (d.date.end != undefined) {
                d.date.end = new Date(d.date.end);
            }

            if (d.date.delay != undefined) {
                d.date.delay = new Date(d.date.delay);
            } else {
                d.date.delay = d.date.end;
            }

            if (d.date.schedule != undefined) {
                d.date.schedule = new Date(d.date.schedule);
            } else {
                d.date.schedule = d.date.start;
            }

            if (!(d.date.start instanceof Date) || !(d.date.end instanceof Date) || d.date.start.getTime() > d.date.end.getTime()) {
                //console.log(d.date.start);
                //console.log(d.date.end);
                console.error("invalid dates in row of dataSet \"" + i + "\" ");
                throw new Exception();
            }
            return d;
        }
        function type2(d, i) {
            //Settando status
            var start = d.date.start.getTime(),
                end = d.date.end.getTime(),
                delay = d.date.delay.getTime();

            if (d.done == true)
                d.status = 4
            else if (now < start)
                d.status = 2
            else if (now <= end && now >= start)
                d.status = 1
            else if (now >= delay)
                d.status = 3
            else
                d.status = 0;
            //Settando Posição - Evitando sobreposição
            var pos = positions.indexOf(null);
            if (pos == -1) {
                positions = positions.map(function (d) {
                    if (d != null && start > d.date.end.getTime())
                        return null;
                    return d;
                });
                var pos = positions.indexOf(null);
                if (pos == -1) {
                    chartConfig.layout.maxrow++;
                    pos = positions.push(null) - 1;//Captura ultimo indice do vetor após a inserção.
                }
            }

            d.position = pos;
            positions[pos] = d;
            return d;

        }

        chartConfig.data = chartConfig.data.map(type);

        function sortByDate(d1, d2) {
            var start1 = d1.date.start.getTime(),
                start2 = d2.date.start.getTime();
            return start1 > start2 ? 1 : (start1 < start2 ? -1 : 0);
        }

        chartConfig.data.sort(sortByDate);

        chartConfig.data = chartConfig.data.map(type2);
        function sortbyStatus(d1, d2) { return d1.status > d2.status ? -1 : (d1.status < d2.status ? 1 : sortByDate(d1, d2)); }
        chartConfig.data.sort(sortbyStatus);

        chartConfig.data = chartConfig.data.map(function (d, i) { d.id = i; return d; });

        //this.chartConfig = ;


        return chartConfig;//this;
    }
    create(chartConfig) {
        var a = this;
        this.chartConfig = chartConfig;
        this.now = chartConfig.now;
        this.svg = a.chartConfig.svg ? d3.select(a.chartConfig.parent) : d3.select(a.chartConfig.parent).append("svg").attr("id", chartConfig.name + "-container")
        if (a.chartConfig.svg)
            this.chartConfig.dimensions.width = +svg.attr("width"),
                this.chartConfig.dimensions.height = +svg.attr("height");
        this.backcolor = "#F5F5F5";
        this.svg.style("background-color", this.backcolor);
        this.pattern = this.svg.append("defs").append("pattern").attr("id", "diagonal-stripe-1")
            .attr("patternUnits", "userSpaceOnUse")
            .attr("width", 10).attr("height", 10)
            .attr("background-color", "#eee");

        this.pattern.append("path")
            .attr("d", "M 0 10 L 12 -2")
            .attr("stroke", "#222")
            .attr("stroke-width", 1);


        this.x = d3.scaleTime();
        this.x2 = d3.scaleTime();
        this.y = d3.scaleBand().domain(range(a.chartConfig.layout.maxrow));
        var temp = d3.extent(a.chartConfig.data, function (d) { return d.date.start; });
        var temp2 = d3.extent(a.chartConfig.data, function (d) { return d.date.end });
        if (a.now.getTime() - temp[0].getTime() < 0) temp[0] = a.now;
        if (a.now.getTime() - temp2[1].getTime() > 0) temp2[1] = a.now;
        this.x.domain([temp[0], temp2[1]]);
        this.x2.domain(this.x.domain());
        this.brush = d3.brushX().on("brush end", function () { a.brushed(a) });
        this.zoom = d3.zoom().scaleExtent([1, Infinity]).on("zoom", function () { a.zoomed(a) });

        this.zoomRect = a.svg.append("rect")
            .attr("class", "zoom").attr("fill", "#FFF").style("cursor", "move").style("fill", "none").style("pointer-events", "all");

        this.focus = a.svg.append("g")
            .attr("class", "focus");
        this.context = a.svg.append("g")
            .attr("class", "context");
        this.focusContent = a.focus.append("g").attr("class", "focuscontextContent");

        this.notifications = a.focusContent.selectAll(".notifications").data(a.chartConfig.data).enter().append("g")
            .style("cursor", "pointer")
            .attr("class", function (d) { return "notifications status-" + d.status });
        this.notifications.append("rect").attr("class", "backBar")
            .style("fill", "url(#diagonal-stripe-1) none")

        this.notifications.append("rect").attr("class", "progressBar")
            .attr("fill", function (d) { return a.chartConfig.layout.colors[d.status] });

        this.nowLine = a.focus.append("g");
        this.nowLine.append("line")
            .attr("fill", "none")
            .attr("stroke", "#222")
            .attr("stroke-width", "2")
            .attr("stroke-dasharray", "5 10");

        this.contextContent = a.context.append("g").attr("class", "contextContent");

        this.card = {}

        this.card.create = function () {
            this.out_dark = a.svg.append("rect")
                .attr("fill", "#000")
                .attr("opacity", 0)
                //.attr("opacity",0.4)
                //.attr("width",a.chartConfig.dimensions.width)
                //.attr("height",a.chartConfig.dimensions.height);
                .attr("width", 0)
                .attr("height", 0)
                .on("click", function () {
                    a.card.disable(0, 500);
                });
            this.all = a.svg.append("g").attr("class", "card");
            //Rects of card
            this.rects = this.all.append("g").attr("class", "cardrects");
            this.rects.append("rect").attr("class", "background")
                .attr("fill", "#fff")
                .attr("stroke-width", "2");
            this.rects.append("rect").attr("class", "backBar")
                .style("fill", "url(#diagonal-stripe-1) " + a.backcolor)
                .attr("stroke-width", 0);
            this.rects.append("rect").attr("class", "progressBar");

            //Content of Card
            this.content = this.all.append("g").attr("class", "cardContent").attr("opacity", 0);
            this.content.append("text").attr("class", "id").attr("opacity", 0);

            //Status Info(Exclamation)
            this.content.append("g").attr("class", "statusInfo");
            this.content.select(".statusInfo").append("rect");
            this.content.select(".statusInfo").append("text").attr("class", "lblstatus")
                .attr("fill", "#FFF")
            this.content.select(".statusInfo").append("g").attr("class", "exclamationContainer");
            //exclamation(this.content.select(".statusInfo").select(.exclamationContainer),100,100,"#FFF");

            // Tittle of Card
            this.content.append("text").attr("class", "tittle")
                .style("font-weight", "bold");
            //.attr("text-anchor", "start");

            // Dates of task (start, end, delay, schedule)
            this.content.append("g").attr("class", "datesInfo");
            //Start
            //End or delay
            //Schedule
            this.content.select(".datesInfo").selectAll("text").data([
                "start", "endOrDelay"//,"schedule"
            ]).enter().append("text").attr("class", function (d) { return d })
                .attr("y", function (d, i) { return "" + i + "em" }).text(function (d) { return d })



            // Percent of done
            this.content.append("g").attr("class", "percentInfo");
            this.content.select(".percentInfo").append("text").attr("class", "info")
                .attr("text-anchor", "start").text("Tarefa já realizada por");
            this.content.select(".percentInfo").append("text").attr("class", "percent")
                .style("font-weight", "bold")
                .attr("text-anchor", "middle");
            this.content.select(".percentInfo").append("text").attr("class", "info")
                .attr("text-anchor", "start").text("dos participantes.");

            // Description (Optional)
            this.content.append("g").attr("class", "desc")
                .attr("text-anchor", "start");

            // Buttons in Botton
            this.content.append("g").attr("class", "buttons");
            this.content.select(".buttons").append("text").attr("class", "or")
                .attr("text-anchor", "middle")
                .style("cursor", "pointer")
                .text("ou")

            // Button schedule
            /*this.content.select(".buttons").append("g").attr("class", "schedule")
                .style("cursor","pointer")
                .append("rect")
                .attr("fill", "#ccc");
            this.content.select(".buttons").select(".schedule").append("text")
                .attr("text-anchor", "middle")
                .attr("dy", "1.25em")
                .attr("fill", "#000")
                .text("Agendar tarefa");*/

            // Button Do task
            this.content.select(".buttons").append("g").attr("class", "goto")
                .style("cursor", "pointer")
                .append("rect")
                .attr("fill", "#ccc");
            this.content.select(".buttons").select(".goto").append("text")
                .attr("text-anchor", "middle")
                .attr("fill", "#000")
                .text("Realizar tarefa");//Acessar Tarefa

            this.content.select(".goto").on("click", function () { var data = a.chartConfig.data[a.card.content.select(".id").text()]; chartConfig.interactions.button(this, data) });



            //this.content.select(".schedule").on("click", function () { var data = a.chartConfig.data[a.card.content.select(".id").text()]; chartConfig.interactions.button(this, data) });

            this.active = false;
        }

        this.card.draw = function () {
            console.log(a.height);
            if (a.chartConfig.dimensions.vertical) {
                if(a.width/2 >300)
                    this.width = 600
                else
                    this.width = a.width;
                this.size = this.width/2;
                this.center = true;
            } else {
                if ((a.height * .7) > 300) {
                    this.size = 300
                } else if ((a.height * .7) < 197) {
                    if (197 > a.chartConfig.dimensions.height)
                        this.size = a.chartConfig.dimensions.height
                    else
                        this.size = 197;
                    this.center = true;
                } else {
                    this.size = a.height * .7;
                }
                this.width = this.size * 6 / 3;
            }
            var y = 0;

            this.all.attr("transform", "translate(" + (-this.width - a.margin.left) + ",0)");



            //Rects of Card
            this.rects.select(".background")
                //.attr("width", this.width)
                //.attr("height", this.size)
                .attr("stroke", "#000")
                .attr("rx", a.y.bandwidth() / 4)
                .attr("ry", a.y.bandwidth() / 4);
            this.rects.select(".backBar")
                //.attr("width", this.width)
                //.attr("height", this.size*.15)
                .attr("stroke", "#000")
                .attr("rx", a.y.bandwidth() / 4)
                .attr("ry", a.y.bandwidth() / 4);
            this.rects.select(".progressBar")
                //.attr("width", this.width*.75)
                //.attr("height", this.size*.15)
                .attr("rx", a.y.bandwidth() / 4)
                .attr("ry", a.y.bandwidth() / 4);

            y += this.size * .15;

            //Status Info(Exclamation)
            this.content.select(".statusInfo")
                .attr("transform", "translate(" + this.width * .5 + "," + this.size * .22 + ")");
            this.content.select(".statusInfo").select("rect")
                .attr("width", this.width * .5)
                .attr("height", this.size * .1);
            this.content.select(".statusInfo").select("text")
                .attr("transform", "translate(" + this.width * .06 + "," + this.size * .075 + ")")
                .attr("font-size", this.size * .05)
                .text("Você perdeu esta tarefa");
            this.content.select(".statusInfo").select(".exclamationContainer")
                .attr("transform", "translate(" + this.width * .01 + "," + this.size * .015 + ")");
            if(!this.exclamationCreated)
                exclamation(this.content.select(".statusInfo").select(".exclamationContainer"), this.size * .08, this.size * .08, "#FFF"),this.exclamationCreated = true;
            else
                exclamationRefatoring(this.content.select(".statusInfo").select(".exclamationContainer"), this.size * .08, this.size * .08, "#FFF");

            // Tittle of Card
            this.content.select(".tittle")
                .attr("font-size", this.size * .08)
                .attr("transform", "translate(" + this.width * .02 + "," + (y + this.size * .15) + ")");

            y += this.size * .15;

            //Dates  of Card
            this.content.select(".datesInfo")
                .attr("transform", "translate(" + this.width * .04 + "," + (y + this.size * .06) + ")")
                .attr("font-size", this.size * .04)
            y += this.size * .06;
            // Percent of done
            this.content.select(".percentInfo")
                .attr("font-size", this.size * .05)
                .attr("transform", "translate(" + this.width * .02 + "," + (y + this.size * .14) + ")");
            this.content.select(".percentInfo").selectAll("text")
                .attr("x", function (d, i) {
                    switch (i) {
                        case 0: return 0;
                        case 1: return a.card.width * .28;
                        case 2: return a.card.width * .32;
                    }
                })

            y += this.size * .14;

            // Description (Optional)
            this.content.select(".desc")
                .attr("font-size", this.size * .04)
                .attr("transform", "translate(" + this.width * .02 + "," + (y + this.size * .03) + ")");
            y += this.size * .03;
            // Buttons in Botton
            this.content.select(".buttons")
                .attr("transform", "translate(0," + this.size * .85 + ")");

            this.content.select(".buttons").select(".or")
                .attr("font-size", this.size * .08)
                .attr("dy", ".9em")
                .attr("transform", "translate(" + this.width * .5 + ",0)");

            this.content.select(".buttons").select(".goto")
                .attr("transform", "translate(" + this.width * .05 + ",0)");
            this.content.select(".buttons").select(".goto").select("rect")
                .attr("width", this.width * .35)
                .attr("height", this.size * .1)
            this.content.select(".buttons").select(".goto").select("text")
                .attr("font-size", this.size * .04)
                .attr("dy", "1.5em")
                .attr("transform", "translate(" + this.width * .175 + ",0)");

            /*this.content.select(".buttons").select(".schedule")
                .attr("transform", "translate(" + this.width * .6 + ",0)");
            this.content.select(".buttons").select(".schedule").select("rect")
                .attr("width", this.width * .35)
                .attr("height", this.size * .1)
            this.content.select(".buttons").select(".schedule").select("text")
                .attr("font-size", this.size * .04)
                .attr("transform", "translate(" + this.width * .175 + ",0)");*/
        }

        this.card.activate = function (data) {
            var b = a.card;
            var before = 0;
            if (b.active != false) {
                before += b.disable(before, 200);
            }
            if (!a.bottomLegend.marked[data.status]) {
                a.filterout();
            }
            before = b.rect_in_x(data, before);
            before = b.extend_card(data, before, 1000);
            b.active = data;
        }

        this.card.disable = function (before, transition) {
            var b = a.card;
            if (b.active == false)
                return
            before = b.rect_in_x(b.active, before, transition);
            b.all
                .transition().delay(before).duration(0)
                .attr("transform", "translate(" + (-b.width) + ",0)");

            b.rects.select(".background")
                .transition().delay(before + 1).duration(0)
                .attr("width", 0)
                .attr("height", 0);
            b.rects.select(".progressBar")
                .transition().delay(before + 1).duration(0)
                .attr("width", 0)
                .attr("height", 0);
            b.rects.select(".backBar")
                .transition().delay(before + 1).duration(0)
                .attr("width", 0)
                .attr("height", 0);

            b.active = false;
            return before + 2;
        }

        this.card.rect_in_x = function (data, before, transition) {
            var b = a.card;
            if (isNaN(before)) before = 0;
            if (isNaN(transition)) transition = 0;
            b.all
                .transition().delay(before).duration(transition)
                .attr("transform", "translate(" + (a.x(data.date.start) + a.margin.left) + "," + (a.y(data.position) + a.margin.top) + ")");

            b.out_dark
                .transition().delay(before).duration(transition)
                .attr("opacity", 0);

            b.out_dark
                .transition().delay(before + transition + 10)
                .attr("width", 0)
                .attr("height", 0);

            b.content
                .transition().delay(before).duration(transition * .2)
                .attr("opacity", 0);

            b.rects.select(".background")
                .transition().delay(before).duration(transition)
                .attr("stroke", a.chartConfig.layout.colors[data.status])
                .attr("width", a.x(data.date.end) - a.x(data.date.start))
                .attr("fill", a.backcolor)
                .attr("height", a.y.bandwidth());
            b.rects.select(".progressBar")
                .transition().delay(before).duration(transition)
                .attr("fill", a.chartConfig.layout.colors[data.status])
                .attr("width", (a.x(data.date.end) - a.x(data.date.start)) * data.percent)
                .attr("height", a.y.bandwidth());
            b.rects.select(".backBar")
                .transition().delay(before).duration(transition)
                .attr("fill", a.backcolor)
                //.attr("fill", a.chartConfig.layout.backcolors[data.status])

                .attr("width", a.x(data.date.end) - a.x(data.date.start))
                .attr("height", a.y.bandwidth());
            return before + transition + 1;
        }

        this.card.reposition = function (x) {
            // Tittle of Card
            this.content.select(".tittle")
                .attr("transform", "translate(" + this.width * .02 + "," + (x + this.size * .15) + ")");

            x += this.size * .15;

            //Dates  of Card
            this.content.select(".datesInfo")
                .attr("transform", "translate(" + this.width * .04 + "," + (x + this.size * .06) + ")")
            x += this.size * .06;
            // Percent of done
            this.content.select(".percentInfo")
                .attr("transform", "translate(" + this.width * .02 + "," + (x + this.size * .14) + ")");

            x += this.size * .14;
        }

        this.card.extend_card = function (data, before, transition) {
            var b = this;

            b.out_dark
                .attr("width", a.chartConfig.dimensions.width)
                .attr("height", a.chartConfig.dimensions.height);

            b.out_dark
                .transition().delay(before).duration(transition)
                .attr("opacity", 0.4)

            if (isNaN(before)) before = 0;
            if (isNaN(transition)) transition = 0;
            var x, y;
            if (b.center) {
                x = (a.chartConfig.dimensions.width - this.width) / 2, y = (a.chartConfig.dimensions.height - this.size) / 2
            } else {
                x = a.x(data.date.start), y = a.y(data.position);
                if (x + b.width > a.width)
                    x = a.width - b.width;
                else if (x < -a.margin.left)
                    x = 0;
                if (y + b.size > a.height)
                    y = a.height - b.size;
            }
            //Rects of card
            b.all
                .transition().delay(before).duration(transition)
                .attr("transform", "translate(" + x + "," + y + ")");
            b.rects.select(".background")
                .transition().delay(before).duration(transition)
                .attr("width", b.width)
                .attr("height", b.size)
                .attr("fill", "#fff");
            b.rects.select(".progressBar")
                .transition().delay(before).duration(transition)
                .attr("width", b.width * data.percent)
                .attr("height", b.size * .15);
            b.rects.select(".backBar")
                .transition().delay(before).duration(transition)
                .attr("width", b.width)
                .attr("height", b.size * .15);
            //Content of Card

            //Status info
            var temp = a.chartConfig.layout.texts2[data.status];
            if (temp != undefined && temp != "") {
                b.content.select(".statusInfo")
                    .attr("transform", "translate(" + b.width + "," + b.size * .22 + ")")
                    .select("rect")
                    .attr("width", 0)
                b.content.select(".statusInfo")
                    .transition().delay(before).duration(transition)
                    .attr("transform", "translate(" + b.width * .5 + "," + b.size * .22 + ")")
                    .attr("opacity", 1);

                b.content.select(".statusInfo").select("rect")
                    .transition().delay(before).duration(transition)
                    .attr("width", b.width * .5)
                    .attr("fill", a.chartConfig.layout.colors[data.status])
                b.content.select(".statusInfo").select("text")
                    .transition().delay(before).duration(transition)
                    .text(temp);
            } else {
                b.content.select(".statusInfo")
                    .transition().delay(before).duration(transition)
                    .attr("opacity", 0);
            }

            // Tittle of Card
            b.content.select(".tittle")
                //.transition().delay(before).duration(transition)
                .text(data.action + " " + data.name);
            //console.log(document.querySelector(".tittle").getBoundingClientRect().width,this.width * .50);
            if (temp != undefined && temp != "" && document.querySelector(".tittle").getBoundingClientRect().width >= this.width * .50) {
                this.reposition(this.size * .27);

            } else {
                this.reposition(this.size * .15);
            }

            //Dates  of Card
            this.content.select(".datesInfo").selectAll("text")
                .transition().delay(before).duration(transition)
                .attr("opacity", function (d, i) {
                    switch (i) {
                        case 0: case 1: return 1;
                        //   case 2:return (!data.done) && data.date.schedule.getTime()>data.date.start.getTime()&&a.chartConfig.now.getTime()<data.date.delay.getTime()?1:0;
                    }
                })
                .attr("fill", function (d, i) {
                    switch (i) {
                        case 0: return "#444";
                        case 1: return data.status == 3 ? "#F00" : "#444";
                        //    case 2:return (a.chartConfig.now.getTime()>=data.date.schedule.getTime()?"#F22":"#444");
                    }
                })
                .text(function (d, i) {
                    var start = data.date.start.toLocaleString(),
                        end = data.date.end,
                        now = a.chartConfig.now;
                    //  schedule = data.date.schedule.toLocaleString();
                    if (end.getTime() < now.getTime()) end = data.date.delay;
                    end = end.toLocaleString();

                    switch (i) {
                        case 0: return "Data/Hora inicial: " + start.substr(0, start.length - 3);
                        case 1: return (data.status == 3 ? "Tarefa encerrada em: " : "Data/Hora final: ") + end.substr(0, start.length - 3);
                        // case 2:return "Sua meta "+(now.getTime()>=data.date.schedule.getTime()?"era":"é")+" realizar em: "+schedule;
                    }
                })

            b.content.select(".percent")
                .transition().delay(before).duration(transition)
                .text(("" + (data.percent * 100)).substr(0, 4) + "%");

            var font = b.size * .04;
            var nletters = b.width * 1.3 / font;
            var textvector = String.linebroke(data.desc, nletters);

            b.content.select(".desc")
                .selectAll("text").remove();

            b.content.select(".desc")
                .selectAll("text").data(textvector).enter().append("text")
                .transition().delay(before).duration(transition)
                .attr("dy", function (d, i) { return "" + (i * 1.3 + 1) + "em" })
                .text(function (d) { return d });

            b.content.select(".id")
                .transition().delay(before).duration(transition)
                .text(data.id);

            if (data.status == 3 || data.status == 4) {
                //this.content.select(".buttons").select(".schedule")
                //.attr("transform", "translate(" + this.width * .325 + ",0)");
                this.content.select(".buttons").select(".goto")
                    .attr("transform", "translate(" + this.width * .325 + ",0)")
                    .select("text").text("ACESSAR TAREFA");
            } else if (data.status == 0 || data.status == 2) {
                //this.content.select(".buttons").select(".schedule")
                //.attr("transform", "translate(" + this.width * .325 + ",0)");
                this.content.select(".buttons").select(".goto")
                    .attr("transform", "translate(" + this.width * .325 + ",0)")
                    .select("text").text("REALIZAR TAREFA");
            } else {
                //this.content.select(".buttons").select(".schedule")
                //.attr("transform", "translate(" + this.width * .6 + ",0)")
                //.select("text").text(function(){
                //   if(data.date.schedule.getTime()>data.date.start.getTime())
                //      return "DEFINIR NOVA META"
                // else
                //    return "DEFINIR META PARA A REALIZAÇÂO"});
                this.content.select(".buttons").select(".goto")
                    .attr("transform", "translate(" + this.width * .325 + ",0)")
                    .select("text").text("REALIZAR TAREFA");
            }

            b.content.transition().delay(before + transition * .7).duration(transition * .3).attr("opacity", 1);




            return before + transition + 1;
        }

        var last = 0, laststatus = 0;
        function searchStatus(status) {
            var data = a.chartConfig.data;
            if (status != laststatus) {
                laststatus = status;
                last = 0;
            }
            var back = false;
            for (var i = last % data.length; true; i = (i + 1) % data.length) {
                if (data[i].status == status) {
                    last = i + 1;
                    return data[i];
                }
                if (back && last == i)
                    return;
                if (last == i)
                    back = true;
            }
            return null;
        }
        var legendConfig = {
            data: a.chartConfig.layout.texts.map(function (d, i) { return { color: a.chartConfig.layout.colors[i], name: d } }),
            target: a.chartConfig.parent,
            svg: a.chartConfig.svg,
            dimensions: {
                width: a.chartConfig.dimensions.width
            },
            layout: {
                corner: 4,
                font_size: 16,
                font: "Roboto",
                //stroke: "#000",
                stroke_width: 2,
                stroke_over: "#a2c",
                anchor: "middle", // start middle end
                //enable_mark:true,
            },
            interactions: {
                mouseover: function (element, data) { },
                mousemove: function (element, data) { },
                mouseout: function (element, data) { },
                click: function (element, data) {
                    var status = a.chartConfig.layout.texts.indexOf(data.name);
                    a.bottomLegend.setoption(data.name);
                    if (a.bottomLegend.marked[status])
                        a.filterout(status, element);
                    else
                        a.filter(status, element);
                    a.card.disable(0, 500);
                    //a.goto(searchStatus(status));
                },
            },
        }


        this.bottomLegend = new BottomLegend(legendConfig);

        /*var legendConfig = {
            name: "legend",
            parent: ".focus",
            svg: true,
            data: {
                name: a.chartConfig.layout.texts,
                color: a.chartConfig.layout.colors
            },
            position: {
                x: a.chartConfig.dimensions.width,
                y: 0,
                align: "top-right"//	top/bottom/middle - left/right/center
            },
            font: {
                name: "sans-serif",
                size: 15,
                align: "start"
            },//	start/end
            interactions: {
                click: function (element, data) {
                    var status = a.chartConfig.layout.texts.indexOf(data);
                    if (a.bottomLegend.marked[status])
                        a.filterout(status, element);
                    else
                        a.filter(status, element);
                    a.card.disable(0, 500);
                    //a.goto(searchStatus(status));
                },
                mouseover: function (element, data) { },
                mousemove: function (element, data) { },
                mouseout: function (element, data) {
                    var status = a.chartConfig.layout.texts.indexOf(data);
                    if (a.bottomLegend.marked[status])
                        d3.select(element).attr("opacity", 0.5);
                }
            }
        }
        this.legend = new Legend(legendConfig);*/
        //this.bottomLegend.marked = a.bottomLegend.marked;

        this.card.create();

        this.notifications.on("click", a.card.activate);

        this.zoomRect
            .on("click", function () {
                a.filterout();
                a.card.disable(0, 500);
            });

        this.context.append("g")
            .attr("class", "axis axis--x context-axis");
        this.focus.append("g")
            .attr("class", "axis axis--x focus-axis")
        this.context.append("g")
            .attr("class", "brush")

        this.contextRects = this.contextContent.selectAll(".testRects").data(a.chartConfig.data).enter().append("rect")
            .attr("class", function (d) { return "testRects status-" + d.status; });

        return this;
    }
    draw() {
        var a = this;
        this.margin = { top: a.chartConfig.margin.top, right: a.chartConfig.margin.right, bottom: a.chartConfig.dimensions.height * a.chartConfig.layout.contextHeight + a.chartConfig.margin.bottom + a.chartConfig.margin.top, left: a.chartConfig.margin.left };
        this.margin2 = { top: a.chartConfig.dimensions.height * (1 - a.chartConfig.layout.contextHeight) - a.chartConfig.margin.bottom, right: a.chartConfig.margin.right, bottom: a.chartConfig.margin.bottom, left: a.chartConfig.margin.left };
        this.width = a.chartConfig.dimensions.width - a.margin.left - a.margin.right;
        this.height = a.chartConfig.dimensions.height - a.margin.top - a.margin.bottom;
        this.height2 = a.chartConfig.dimensions.height - a.margin2.top - a.margin2.bottom;

        this.svg
            .attr("width", a.chartConfig.dimensions.width)
            .attr("height", a.chartConfig.dimensions.height)
        //console.log(this.margin);
        //console.log(this.margin2);
        //console.log("w:",a.width,"h:",a.height);
        //console.log("w:",a.chartConfig.dimensions.width,"h:",a.chartConfig.dimensions.height);
        this.x.range([0, a.width]),
            this.x2.range([0, a.width]),
            this.y.rangeRound([0, a.height]).padding(a.height > 300 ? 0.4 : 0.1);

        this.nowLine.select("line")
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", 0)
            .attr("y2", a.height);

        this.xAxis = d3.axisBottom(this.x).ticks(Math.floor(a.chartConfig.dimensions.width / 70));
        this.xAxis2 = d3.axisBottom(this.x2).ticks(Math.floor(a.chartConfig.dimensions.width / 70));

        this.brush.extent([[0, 0], [a.width, a.height2]]);

        this.zoom.translateExtent([[0, 0], [a.width, a.height]])
            .extent([[0, 0], [a.width, a.height]]);

        this.focus.attr("transform", "translate(" + a.margin.left + "," + a.margin.top + ")");

        this.context.attr("transform", "translate(" + a.margin2.left + "," + a.margin2.top + ")");

        this.notifications.select(".backBar")
            .attr("rx", a.y.bandwidth() / 4)
            .attr("ry", a.y.bandwidth() / 4);

        this.notifications.select(".progressBar")
            .attr("rx", a.y.bandwidth() / 4)
            .attr("ry", a.y.bandwidth() / 4);

        this.transformElements();



        this.focus.select(".focus-axis")
            .attr("transform", "translate(0," + a.height + ")")
            .call(a.xAxis);

        function widthRect(data) {
            return a.x2(data.date.end) - a.x2(data.date.start);
        }

        this.contextRects
            .attr("transform", function (d) { return "translate(" + a.x2(d.date.start) + ",0)" })
            .attr("width", widthRect)
            .attr("height", a.height2)
            .attr("rx", a.height2 / 3 > 10 ? 10 : a.height2 / 3)
            .attr("ry", a.height2 / 3 > 10 ? 10 : a.height2 / 3)
            .attr("stroke", "#ddd")
            .attr("stroke-width", ".5")
            .attr("fill", function (d) { return a.chartConfig.layout.colors[d.status] });;

        this.context.select(".context-axis")
            .attr("transform", "translate(0," + a.height2 + ")")
            .call(a.xAxis2);

        this.context.select(".brush")
            .call(a.brush)
            .call(a.brush.move, a.x.range());

        this.zoomRect
            .attr("width", a.width)
            .attr("height", a.height)
            .attr("transform", "translate(" + a.margin.left + "," + a.margin.top + ")")
            .call(a.zoom);
        this.card.draw();

        this.filterout();
        this.reset();

        return this;
    }
    static definewidth(chartConfig){
        if (chartConfig.dimensions == undefined) chartConfig.dimensions = {};
        chartConfig.dimensions.vertical = false;
        if (chartConfig.dimensions.width == undefined) {
            var temp;
            if (temp = document.querySelector(chartConfig.parent).getBoundingClientRect()) {
                chartConfig.dimensions.width = temp.width;
                var prop = window.innerHeight * .6 / window.innerWidth;
                console.log(prop);
                if (window.innerWidth > 991)
                    chartConfig.dimensions.height = temp.width / 2 > 500 ? 500 : temp.width / 2
                else
                    chartConfig.dimensions.height = temp.width * prop, chartConfig.dimensions.vertical = prop/0.6>1;
            }
            else if (chartConfig.dimensions.height == undefined)
                chartConfig.dimensions.width = 1200, chartConfig.dimensions.height = 500;
            else
                chartConfig.dimensions.width = chartConfig.dimensions.height * 12 / 5;
        }
        if (chartConfig.dimensions.height == undefined)
            chartConfig.dimensions.height = chartConfig.dimensions.width * 5 / 12;
    }
    resize(width, height) {
        var a = this;
        a.chartConfig.dimensions.width = width,
        a.chartConfig.dimensions.height = height;
        GanttChart.definewidth(a.chartConfig);
        this.draw();
        return this;
    }
    filter(status, element) {
        var a = this;
        //a.bottomLegend.marked[status] = true;
        a.svg.selectAll(".notifications").transition().duration(500).attr("opacity", 0.2)
        a.svg.selectAll(".testRects").transition().duration(500).attr("opacity", 0.05)
        if (a.bottomLegend.marked.indexOf(true) == -1 || a.bottomLegend.marked.indexOf(false) == -1)
            a.filterout();
        else {
            a.bottomLegend.marked.map(function (d, i) {
                if (d) {
                    a.svg.selectAll(".status-" + i).transition().duration(500).attr("opacity", 1)
                }
            });
            a.bottomLegend.legend/*.attr("opacity", function(d,i){
                if(a.bottomLegend.marked[i]==true)
                    return 0.5;
                else   
                    return 1;
            })*/.attr("style", function (d, i) {
                if (a.bottomLegend.marked[i] == true)
                    return "cursor:url('" + a.chartConfig.cursors.subber + "'),auto";
                else
                    return "cursor:url('" + a.chartConfig.cursors.adder + "'),auto";
            });
        }

    }
    filterout(status, element) {
        var a = this;
        if (status != undefined) {
            //a.bottomLegend.marked[status] = false;
            if (a.bottomLegend.marked.indexOf(true) == -1 || a.bottomLegend.marked.indexOf(false) == -1)
                a.filterout();
            else {
                a.bottomLegend.marked.map(function (d, i) {
                    if (d == false) {
                        a.svg.selectAll(".notifications.status-" + i).transition().duration(500).attr("opacity", 0.2)
                        a.svg.selectAll(".testRects.status-" + i).transition().duration(500).attr("opacity", 0.05)
                    }
                });
                a.bottomLegend.legend/*.attr("opacity", function(d,i){
                    if(a.bottomLegend.marked[i]==true)
                        return 0.5;
                    else   
                        return 1;
                })*/.attr("style", function (d, i) {
                    if (a.bottomLegend.marked[i] == true)
                        return "cursor:url('" + a.chartConfig.cursors.subber + "'),auto";
                    else
                        return "cursor:url('" + a.chartConfig.cursors.adder + "'),auto";
                });
            }
        } else {
            //a.bottomLegend.marked = a.bottomLegend.marked.map(function () { return false });
            a.bottomLegend.setoption();
            a.bottomLegend.legend/*.attr("opacity",1)*/.attr("style", "cursor:url('" + a.chartConfig.cursors.filter + "'),auto");
            a.svg.selectAll(".notifications").transition().duration(500).attr("opacity", 1);
            a.svg.selectAll(".testRects").transition().duration(500).attr("opacity", 1);
        }
    }
    goto(data, period) {
        if (!data)
            return;
        var a = this;
        this.gotoperiod(data.date.start, data.date.end, period);
        a.card.activate(data);
    }
    gotoperiod(init, end, period) {
        var a = this;
        if (period == undefined)
            period = 10;
        var s = [
            new Date(init.getFullYear(), init.getMonth(), init.getDate() - period),
            new Date(end.getFullYear(), end.getMonth(), end.getDate() + period)
        ];
        s = s.map(function (d) {
            var temp = a.x2(d);
            return temp < 0 ? 0 : (temp > a.x2.range()[1] ? a.x2.range()[1] : temp);
        });
        a.x.domain(s.map(a.x2.invert, a.x2));

        a.focus.select(".axis--x").call(a.xAxis);

        a.svg.select(".zoom").call(a.zoom.transform, d3.zoomIdentity
            .scale(a.width / (s[1] - s[0]))
            .translate(-s[0], 0));

    }
    reset(period) {
        var a = this;
        if (period == undefined)
            period = 10;
        var s = [new Date(a.now.getFullYear(), a.now.getMonth(), a.now.getDate() - period),
        new Date(a.now.getFullYear(), a.now.getMonth(), a.now.getDate() + period)];
        s = s.map(function (d) {
            var temp = a.x2(d);
            return temp < 0 ? 0 : (temp > a.x2.range()[1] ? a.x2.range()[1] : temp);
        });

        a.x.domain(s.map(a.x2.invert, a.x2));

        a.focus.select(".axis--x").call(a.xAxis);

        a.transformElements(500);

        a.svg.select(".zoom").call(a.zoom.transform, d3.zoomIdentity
            .scale(a.width / (s[1] - s[0]))
            .translate(-s[0], 0));
    }
    zoomed(a, transition) {
        if (a.card.active) {
            a.card.disable(0, 500);
        }
        if (d3.event.sourceEvent && d3.event.sourceEvent.type === "brush") return; // ignore zoom-by-brush
        var t = d3.event.transform;
        temp = t;
        a.x.domain(t.rescaleX(a.x2).domain());

        a.focus.select(".axis--x").call(a.xAxis);
        //if(isNaN(a.temptransition))
        //a.temptransition = 200;
        this.transformElements();

        a.context.select(".brush").call(a.brush.move, a.x.range().map(t.invertX, t));
    }
    brushed(a) {
        if (a.card.active) {
            a.card.disable(0, 500);
        }
        if (d3.event.sourceEvent && d3.event.sourceEvent.type === "zoom") return; // ignore brush-by-zoom
        var s = d3.event.selection || a.x2.range();
        temp2 = s;
        a.x.domain(s.map(a.x2.invert, a.x2));

        a.focus.select(".axis--x").call(a.xAxis);
        //var transition = a.temptransition;
        //a.temptransition = 0;
        a.transformElements();

        a.svg.select(".zoom").call(a.zoom.transform, d3.zoomIdentity
            .scale(a.width / (s[1] - s[0]))
            .translate(-s[0], 0));
        //a.temptransition = transition;
    }
    transformElements(transition) {
        if (isNaN(transition))
            transition = 0;
        var a = this;
        function widthRect(data) {
            return a.x(data.date.end) - a.x(data.date.start);
        }
        function transformRect(data, i) {
            return "translate(" + (a.x(data.date.start)) + "," + a.y(data.position) + ")";
        }

        a.notifications
            //.transition().duration(transition)
            .attr("transform", transformRect)
        a.notifications.select(".backBar")
            //.transition().duration(transition)
            .attr("width", widthRect)
            .attr("height", a.y.bandwidth());
        a.notifications.select(".progressBar")
            //.transition().duration(transition)
            .attr("width", function (d) { return widthRect(d) * d.percent })
            .attr("height", a.y.bandwidth());

        a.nowLine.transition().duration(transition).attr("transform", "translate(" + a.x(a.now) + ",0)");

    }

}

var multiGanttCont = 0;
class MultiGanttChart {
    constructor(data) {
        this.create(data).draw();
    }
    create(data) {
        var a = this;
        this.subjects = data.map(function (d, i) {
            if (d.name == undefined) d.name = "auto-subject" + i;
            if (d.chartConfig == undefined) d.chartConfig = {};
            d.chartConfig.data = d.data;
            d.chartConfig = GanttChart.validData(d.chartConfig);
            return d;
        });

        var a = this;
        this.svg = data.svg ? d3.select(data.target) : d3.select(data.target).append("svg").attr("id", "multiganttt");
        this.now = new Date();


        return this;
    }
    draw() {



    }
}
