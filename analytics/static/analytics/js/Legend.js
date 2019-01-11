var contLegend = 0;

/**
 * Legend Class sample
 * var legendConfig = {
		name:"legend",
		parent:"#chartSvg",
		svg:true,
		data:{	name:["value","value4","value3","value2"],
		    	color:["#98abc5", "#7b6888", "#a05d56", "#ff8c00"]},
		position:{
		    	//x:380,
		    	//y:280,
		    	//align:"bottom-right"//	top/bottom/middle - left/right/center
		},
		font:{
		    	name:"sans-serif",
		    	size: 15,
		    	align:"start"},//	start/end
		interactions:{
		    	click: function(element,data){},
		    	mouseover: function(element,data){},
		    	mousemove: function(element,data){},
		    	mouseout: function(element,data){}}
	}
	var legend = new Legend(legendConfig);
 * */

class Legend {
	constructor(legendConfig) {
		this.validData(legendConfig).create().draw().addInteractions();
	}
	validData(legendConfig) {
		var a = this;
		if (legendConfig.data == undefined || legendConfig.data.name == undefined || legendConfig.data.color == undefined) {
			console.error("Impossible create legend without DataSource");
			return;
		}
		if (legendConfig.data.name.length > legendConfig.data.color.length) {
			console.error("Impossible create legend with incompatible DataSource");
			return;
		}
		if (legendConfig.parent == undefined) {
			console.error("Impossible create legend without SVG container");
			return;
		}
		if (legendConfig.name == undefined) {
			legendConfig.name = "legend" + contLegend++;
		}

		if (legendConfig.font == undefined) legendConfig.font = {};
		if (legendConfig.font.name == undefined) legendConfig.font.name = "sans-serif";
		if (legendConfig.font.size == undefined) legendConfig.font.size = 15;
		if (legendConfig.font.align == undefined) legendConfig.font.align = "end";

		if (legendConfig.svg == undefined) legendConfig.svg = false;
		this.svg = legendConfig.svg ?
			d3.select(legendConfig.parent) :
			d3.select(legendConfig.parent)
				.append("svg")
				.attr("id", legendConfig.name + "-container");

		if (legendConfig.position == undefined) legendConfig.position = {};
		if (legendConfig.position.align == undefined) legendConfig.position.align = "top-left";
		this.legendConfig = legendConfig;
		if (a.legendConfig.position.x != undefined)
			a.legendConfig.position.xok = true;
		if (a.legendConfig.position.y != undefined)
			a.legendConfig.position.yok = true;
		if (a.legendConfig.svg)
			this.validXY();

		legendConfig.interactions = d3.validEvents(legendConfig.interactions);

		return this;
	}
	create() {
		var a = this;

		this.g = this.svg.append("g").attr("id", this.legendConfig.name);

		this.ancor = this.g.append("g");

		this.background = this.ancor.append("rect")
			.attr("fill", "#FFF");

		this.legendG = this.ancor.append("g").attr("id", a.legendConfig.name + "-inner").attr("font-family", this.legendConfig.font.name);

		this.legend = this.legendG.selectAll("g").data(this.legendConfig.data.name).enter()
			.append("g");
		this.legend.append("text").text(function (d) {
			return d;
		}).attr("dy", "0.85em");
		this.legend.append("rect").attr("fill", function (d, i) {
			return a.legendConfig.data.color[i];
		});
		return this;
	}
	draw() {
		var a = this;
		this.legendG.attr("font-size", this.legendConfig.font.size).attr("text-anchor", "start");

		this.background.attr("transform", "translate(0,0)")
			.attr("width", 0)
			.attr("height", 0);

		this.legend.attr("transform", function (d, i) {
			return "translate(0," + i * (a.legendConfig.font.size + 3) + ")";
		});

		this.legend.select("rect")
			.attr("width", this.legendConfig.font.size)
			.attr("height", this.legendConfig.font.size)
			.attr("x", -this.legendConfig.font.size - 3);


		var legendDimensions = document.getDimensions("#" + this.legendConfig.name + "-inner");

		this.legendDimensions = legendDimensions;

		if (!a.legendConfig.svg) {
			this.svg
				.attr("width", a.legendDimensions.w)
				.attr("height", a.legendDimensions.h)
		}

		this.validXY();

		this.g.attr("transform", "translate(" + this.legendConfig.position.x + "," + this.legendConfig.position.y + ")");

		var ancorConfig = this.legendConfig.position.align.split("-");
		this.legendG.attr("text-anchor", a.legendConfig.font.align);

		this.ancor.attr("transform", function () {
			var x, y;
			switch (ancorConfig[1]) {
				case "center": x = -legendDimensions.w / 2; break;//a.svg.attr("width")/2
				case "right": x = -legendDimensions.w; break;
				default: x = 0; break;
			}
			switch (ancorConfig[0]) {
				case "middle": y = -legendDimensions.h / 2; break;//a.svg.attr("height")/2
				case "bottom": y = -legendDimensions.h; break;
				default: y = 0; break;
			}
			return "translate(" + x + "," + y + ")";
		});

		this.legend.selectAll("text")
			.attr("x", function () {
				switch (a.legendConfig.font.align) {
					case "end": return a.legendDimensions.w - a.legendConfig.font.size - 3;
					default: return a.legendConfig.font.size + 3;
				}
			});

		this.legend.selectAll("rect")
			.attr("x", function () {
				switch (a.legendConfig.font.align) {
					case "end": return a.legendDimensions.w - a.legendConfig.font.size;
					default: return 0;
				}
			});

		this.background.attr("width", a.legendDimensions.w)
			.attr("height", a.legendDimensions.h).attr("transform", "translate(0,0)");/**/



		return this;
	}
	validXY() {
		var a = this;
		var ancorConfig = a.legendConfig.position.align.split("-");
		if (!a.legendConfig.position.xok)
			switch (ancorConfig[1]) {
				case "center": a.legendConfig.position.x = a.svg.attr("width") / 2; break;
				case "right": a.legendConfig.position.x = a.svg.attr("width"); break;
				default: a.legendConfig.position.x = 0; break;
			}

		if (!a.legendConfig.position.yok)
			switch (ancorConfig[0]) {
				case "middle": a.legendConfig.position.y = a.svg.attr("height") / 2; break;
				case "bottom": a.legendConfig.position.y = a.svg.attr("height"); break;
				default: a.legendConfig.position.y = 0; break;
			}

		return this;
	}
	resize(val) {
		this.legendConfig.font.size = val;
		return this.draw();
	}
	translate(x, y) {
		if (x != undefined)
			this.legendConfig.position.x = x;
		if (y != undefined)
			this.legendConfig.position.y = y;
		return this.move();
	}
	move(x, y) {
		if (x == undefined)
			x = this.legendConfig.position.x;
		if (y == undefined)
			y = this.legendConfig.position.y;
		this.g.transition().duration(500)
			.attr("transform", "translate(" + x + "," + y + ")");
		return this;
	}
	addInteractions() {
		var a = this;
		a.legendConfig.interactions.mouseout.push(function (element, data) {
			var currentEl = d3.select(element);
			currentEl.attr("opacity", 1);
		});
		a.legendConfig.interactions.mouseover.push(function (element, data) {
			var currentEl = d3.select(element);
			currentEl.attr("opacity", 0.5);
		});
		d3.addEvents(a.legend, a.legendConfig.interactions);

		return this;
	}
}

/*var chartConfig = {
	data:[
		{id:0,color:"#F00",name:"Vermelho"},
		{id:1,color:"#0F0",name:"Verde"},
		{id:2,color:"#00F",name:"Azul"},
	],
	target:"body",
	svg:false,
	dimensions:{
		width:800
	},
	layout:{
		corner:4,
		font_size:16,
		rect_size:20,
		font: "roboto",
		stroke: "#000",
		stroke_width: 2,
		stroke_over: "#ccc",
		anchor: "middle" // start middle end
		enable_mark:true,
	},
	interactions:{
		mouseover:function(element,data){},
		mousemove:function(element,data){},
		mouseout:function(element,data){},
		click:function(element,data){},
	},
}*/

var bottomLegendCount = 0;
class BottomLegend{
	constructor(chartConfig){
		this.create(BottomLegend.validData(chartConfig)).draw();
	}
	static validData(chartConfig){
		if(chartConfig==undefined || chartConfig.data == undefined){
			console.error("DataSet Invalid");
			throw new Exception();
		}
		if(chartConfig.target == undefined)chartConfig.target = "body";
		if(chartConfig.dimensions == undefined)chartConfig.dimensions = {};
		if(chartConfig.dimensions.width == undefined){
			if(chartConfig.svg)
				chartConfig.dimensions.width = d3.select(chartConfig.target).attr("width");
			else
			chartConfig.dimensions.width = 800;
		}
		
		if(chartConfig.layout == undefined)chartConfig.layout = {};
		if(chartConfig.layout.corner == undefined)chartConfig.layout.corner = 4;
		if(chartConfig.layout.font_size == undefined)chartConfig.layout.font_size = 16;
		if(chartConfig.layout.rect_size == undefined)chartConfig.layout.rect_size = chartConfig.layout.font_size*1.25
		if(chartConfig.layout.font == undefined)chartConfig.layout.font = "Roboto";
		if(chartConfig.layout.stroke_width == undefined)chartConfig.layout.stroke_width = 2;
		if(!isColor(chartConfig.layout.stroke))chartConfig.layout.stroke = undefined;
		if(!isColor(chartConfig.layout.stroke_over))chartConfig.layout.stroke_over = undefined;
		if(chartConfig.layout.anchor!="start" && chartConfig.layout.anchor!= "end")chartConfig.layout.anchor = "middle";
		
		chartConfig.interactions = d3.validEvents(chartConfig.interactions);
		var id = undefined;
		var type = [
			function(d,i){
				if(!isColor(d.color) || typeof d.name != "string"){
					console.error("invalid row \""+i+"\"");
					throw new Exception();
				}
				id = isNaN(d.id)||d.id<=id?id:d.id;
				if(id == undefined)
					id = -1;
				return d;
			},
			function(d){
				if(isNaN(d.id))
					d.id = ++id;
				return d;
			}
		];

		chartConfig.data = treatData(chartConfig.data,type);
		return chartConfig;
	}
	create(chartConfig){
		var a = this;
		this.chartConfig = chartConfig;
		this.name = "bottom-legend-"+bottomLegendCount++;
		this.svg = a.chartConfig.svg?d3.select(a.chartConfig.target):d3.select(a.chartConfig.target).append("svg");
		this.g = a.svg.append("g").attr("id",this.name + "-g");
		
		this.axis = d3.scaleBand().padding(0.1);

		this.marked = range(a.chartConfig.data.length).map(function(){return false});

		return this;
	}
	setoption(data){
		var a = this;
		if(data == undefined){
			this.marked = this.marked.map(function(){return false});
			a.g.selectAll(".legend").select(".anchor").select(".clips").transition().delay(110).duration(100).attr("opacity",0);
			return;
		}
			
		a.chartConfig.data.map(function(d,i){
			if(!isNaN(data) && data == i){
				a.marked[i] = !a.marked[i];
				a.g.select(".legend-"+i).select(".anchor").select(".clips").transition().duration(100).attr("opacity",a.marked[i]?1:0);
			}else if(isColor(data) && data == d.color){
				a.marked[i] = !a.marked[i];
				a.g.select(".legend-"+i).select(".anchor").select(".clips").transition().duration(100).attr("opacity",a.marked[i]?1:0);
			}else if(typeof data == "string" && data == d.name){
				a.marked[i] = !a.marked[i];
				a.g.select(".legend-"+i).select(".anchor").select(".clips").transition().duration(100).attr("opacity",a.marked[i]?1:0);
			}
		})

		if(a.marked.indexOf(false)== -1)
			this.setoption();
	}
	draw(){
		var a = this;
		this.define_disposition();

		this.svg.attr("width",a.chartConfig.dimensions.width)
				.attr("height",a.chartConfig.layout.rect_size*1.1*this.disposition.length+a.chartConfig.layout.rect_size/2);

		this.axis.domain(range(this.disposition.length)).range([0,a.chartConfig.layout.rect_size*1.1*this.disposition.length]);

		this.row = a.g.selectAll(".row").data(this.disposition);

		this.row.exit().transition().duration(500).attr("opacity",0);
		this.row.exit().transition().delay(510).remove();

		this.row = this.row.enter().append("g").attr("class","row")
			.attr("transform",function(d,i){return "translate("+(d.dx?a.space/2:0)+","+a.axis(i)+")"});

		this.legend = this.row.selectAll(".legend").data(function(d,i){return a.disposition[i]});
		this.legend.exit().transition().duration(500).attr("opacity",0);
		this.legend.exit().transition().delay(510).remove();

		this.legend = this.legend.enter().append("g")
			.attr("class",function(d,i){return "legend legend-"+i;})
			.attr("transform",function(d,i){return "translate("+i*a.space+",0)"});

		this.legend.append("g").attr("class","anchor");

		this.legend.select(".anchor").append("rect")
			.attr("width",a.chartConfig.layout.rect_size)
			.attr("height",a.chartConfig.layout.rect_size)
			.attr("rx",a.chartConfig.layout.corner)
			.attr("ry",a.chartConfig.layout.corner)
			.attr("fill",function(d){return d.color})
			.attr("stroke-width",a.chartConfig.layout.stroke_width)
			.attr("stroke",a.chartConfig.layout.stroke)
			.style("box-shadow","0px 2px 2px rgba(0, 0, 0, 0.05)");

		this.legend.select(".anchor").append("text")
			.style("font-family",a.chartConfig.layout.font)
			.style("font-size",""+a.chartConfig.layout.font_size+"px")
			.style("font-style","normal")
			.style("font-weight","300")
			.style("line-height","normal")
			.attr("x",a.chartConfig.layout.rect_size*1.25)
			.attr("y",a.chartConfig.layout.rect_size*.25)
			.attr("dy",".6em")
			.text(function(d){return d.name});
		this.legend.select(".anchor").append("g").attr("class","clips")
			.attr("transform","translate("+a.chartConfig.layout.rect_size*.15+",0)").attr("opacity",0)
		paperClip(this.legend.select(".anchor").select(".clips"),20,30,a.chartConfig.layout.stroke_over)

		if(a.chartConfig.layout.stroke_over){
			this.chartConfig.interactions.mouseover.push(function(element,data){
				d3.select(element).select("rect").attr("stroke",a.chartConfig.layout.stroke_over);
			});
			this.chartConfig.interactions.mouseout.push(function(element,data){
				d3.select(element).select("rect").attr("stroke",a.chartConfig.layout.stroke);
			});
		}
		if(a.chartConfig.layout.enable_mark){
			this.chartConfig.interactions.click.push(function(element,data){
				a.setoption(data.name);
			});
		}

		d3.addEvents(this.legend,a.chartConfig.interactions);
		
		

		this.g.attr("transform","translate("+(a.chartConfig.dimensions.width-document.querySelector("#"+this.name+"-g").getBoundingClientRect().width)/2+",0)");

			

		return this;
	}
	define_disposition(){
		var a = this;

		this.legend = a.g.selectAll(".legend").data(this.chartConfig.data).enter().append("g")
			.attr("class","legend");

		this.legend.append("g").attr("class","anchor");
		this.legend.select(".anchor").append("rect")
			.attr("width",a.chartConfig.layout.rect_size)
			.attr("height",a.chartConfig.layout.rect_size)
			.attr("rx",a.chartConfig.layout.corner)
			.attr("ry",a.chartConfig.layout.corner)
			.attr("fill",function(d){return d.color})
			.attr("stroke-width",a.chartConfig.layout.stroke_width)
			.style("box-shadow","0px 2px 2px rgba(0, 0, 0, 0.05)");


		this.legend.select(".anchor").append("text")
			.style("font-family",a.chartConfig.layout.font)
			.style("font-size",""+a.chartConfig.layout.font_size+"px")
			.style("font-style","normal")
			.style("font-weight","300")
			.style("line-height","normal")
			.attr("x",a.chartConfig.layout.rect_size*1.25)
			.attr("y",a.chartConfig.layout.rect_size*.25)
			.attr("dy",".6em")
			.text(function(d){return d.name});

		var max = 0;
		var legends = document.querySelector(a.chartConfig.target).querySelectorAll(".legend");
		for(var i=0;i<legends.length;i++){
			a.chartConfig.data[i].width = legends[i].getBoundingClientRect().width;
		}
		legends = a.chartConfig.data;
		
		for(var i=0;i<legends.length;i++){
			var temp = legends[i].width;
			max = max>temp?max:temp;
		}
		legends = [legends];
		this.space = max*1.4;
		var limt = max*1.1;
		var keep = true;
		var width = this.chartConfig.dimensions.width;

		function partvector(vector){
			if(vector[0].length<=1){
				return vector;
			}
			var size = vector.length+1;
			for(var i=1;i<vector.length;i++){
				vector[0] = vector[0].concat(vector[i]);
			}
			var temp = vector[0].length%size;
			var slice = parseInt(vector[0].length/size);
			var ret = [];
			for(var i=0;i<size;i++){
				ret.push(vector[0].slice(i*slice+(i>=temp?temp:i),(i+1)*slice+(i>=temp?temp:(i+1))));
				if(temp!=0 && i>=temp)
					ret[ret.length].dx = true;
			}
			return ret;
		}		

		while(keep){
			if(legends[0].length*this.space>width)
				if(width/legends[0].length >limit){
					this.space = width/legends[0].length;
					keep = false;
				}else{
					var temp = legends.length;
					legends = partvector(legends);
					if (temp == legends.length)
						keep = false;
				}
			else{
				keep = false;
			}
		}
		this.legend.remove();
		this.disposition = legends;
		return this;
	}
}