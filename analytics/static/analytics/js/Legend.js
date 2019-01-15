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
		right:false, // true - RightLegend; false - BottomLegend;
		width:800,
		height:600,
		x:0,
		y:0,
	},
	layout:{
		corner:4,
		padding: 0.4,
		font_size:16,
		rect_size:20,
		font: "roboto",
		stroke: "#000",
		stroke_width: 2,
		stroke_over: "#ccc",
		enable_mark:true,
	},
	interactions:{
		mouseover:function(element,data){},
		mousemove:function(element,data){},
		mouseout:function(element,data){},
		click:function(element,data){},
		filter:function(element, data){},
		unfilter: function(element, data){},
		unfilterAll: function(){}
	},
}*/

var bottomLegendCount = 0;
class BottomLegend{
	constructor(chartConfig){
		this.create(BottomLegend.validData(chartConfig)).draw();
	}
	static validData(chartConfig,preconfig){
		if(!preconfig&&(chartConfig==undefined || chartConfig.data == undefined)){
			console.error("DataSet Invalid");
			throw new Exception();
		}
		if(preconfig && chartConfig==undefined)
			chartConfig = preconfig;

		if(chartConfig.target == undefined)chartConfig.target = preconfig?preconfig.target:"body";
		if(chartConfig.dimensions == undefined)chartConfig.dimensions = preconfig?preconfig.dimensions:{};

		if(!chartConfig.dimensions.right==undefined)chartConfig.dimensions.right = preconfig?preconfig.dimensions.right:undefined;

		if(!chartConfig.dimensions.right){
			if(chartConfig.dimensions.width == undefined || chartConfig.dimensions.width=="auto"){
				var temp;
				if(preconfig && !preconfig.dimensions.right && chartConfig.dimensions.width=="auto")
					chartConfig.dimensions.width = preconfig.dimensions.width;
				else if(temp = document.querySelector(chartConfig.target).getBoundingClientRect.width)
					chartConfig.dimensions.width = temp;
				else
					chartConfig.dimensions.width = 800;
			}
		}else{
			if(chartConfig.dimensions.height == undefined || chartConfig.dimensions.height=="auto"){
				var temp;
				if(preconfig && preconfig.dimensions.right && chartConfig.dimensions.height=="auto")
					chartConfig.dimensions.height = preconfig.dimensions.height;
				else if(temp = document.querySelector(chartConfig.target).getBoundingClientRect.height)
					chartConfig.dimensions.height = temp;
				else
					chartConfig.dimensions.height = 600;
			}
		}
		if(chartConfig.dimensions.x == undefined)chartConfig.dimensions.x = preconfig?preconfig.dimensions.x:0;
		if(chartConfig.dimensions.y == undefined)chartConfig.dimensions.y = preconfig?preconfig.dimensions.y:0;

		
		if(chartConfig.layout == undefined)chartConfig.layout = preconfig?preconfig.layout:{};
		if(chartConfig.layout.corner == undefined)chartConfig.layout.corner = preconfig?preconfig.layout.corner:4;
		if(chartConfig.layout.padding == undefined)chartConfig.layout.padding = preconfig?preconfig.layout.padding:0.4;
		if(chartConfig.layout.font_size == undefined)chartConfig.layout.font_size = preconfig?preconfig.layout.font_size: 16;
		if(chartConfig.layout.rect_size == undefined)chartConfig.layout.rect_size = preconfig?preconfig.layout.rect_size : chartConfig.layout.font_size*1.25
		if(chartConfig.layout.font == undefined)chartConfig.layout.font = preconfig?preconfig.layout.font: "Roboto";
		if(chartConfig.layout.stroke_width == undefined)chartConfig.layout.stroke_width = preconfig?preconfig.layout.stroke_width:2;
		if(!isColor(chartConfig.layout.stroke))chartConfig.layout.stroke = preconfig?preconfig.layout.stroke : undefined;
		if(!isColor(chartConfig.layout.stroke_over))chartConfig.layout.stroke_over = preconfig?preconfig.layout.stroke_over: undefined;
		if(preconfig){
			if(chartConfig.interactions!= undefined){
				if(chartConfig.interactions.click)
					preconfig.interactions.click.push(chartConfig.interactions.click);
				if(chartConfig.interactions.mouseover)
					preconfig.interactions.mouseover.push(chartConfig.interactions.mouseover);
				if(chartConfig.interactions.mousemove)
					preconfig.interactions.mousemove.push(chartConfig.interactions.mousemove);
				if(chartConfig.interactions.mouseout)
					preconfig.interactions.mouseout.push(chartConfig.interactions.mouseout);
				if(chartConfig.interactions.filter)
					preconfig.interactions.filter = chartConfig.interactions.filter;
				if(chartConfig.interactions.unfilter)
					preconfig.interactions.unfilter = chartConfig.interactions.unfilter;
				if(chartConfig.interactions.unfilterAll)
					preconfig.interactions.unfilterAll = chartConfig.interactions.unfilterAll;
			}
			chartConfig.interactions = preconfig.interactions;
		}else
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
		if(preconfig && chartConfig.data == undefined)
			chartConfig.data = preconfig.data;
		else
			chartConfig.data = treatData(chartConfig.data,type);
		return chartConfig;
	}
	create(chartConfig){
		var a = this;
		this.chartConfig = chartConfig;
		this.name = "bottom-legend-"+bottomLegendCount++;
		this.svg = a.chartConfig.svg?d3.select(a.chartConfig.target):d3.select(a.chartConfig.target).append("svg").attr("id",this.name);
		this.g = a.svg.append("g").attr("id",this.name + "-g");
		
		this.axis = d3.scaleBand().padding(a.chartConfig.layout.padding);

		this.marked = range(a.chartConfig.data.length).map(function(){return false});

		return this;
	}
	redraw(chartConfig){
		var a = this;
		this.chartConfig = BottomLegend.validData(chartConfig,this.chartConfig);
		this.draw();
		return this;
	}
	resize(size){
		var width,height;
		if(this.chartConfig.dimensions.right)
			height = size?size:document.querySelector(this.chartConfig.target).getBoundingClientRect().height;
		else
			width = size?size:document.querySelector(this.chartConfig.target).getBoundingClientRect().width;
		this.chartConfig.dimensions.width = width;
		this.chartConfig.dimensions.height = height;
		this.draw();
		return this;
	}
	setoption(data){
		var a = this;
		if(data == undefined){
			this.marked = this.marked.map(function(){return false});
			a.g.selectAll(".legend").select(".anchor").select(".muralpin").transition().delay(110).duration(100).attr("opacity",0);
			if(a.chartConfig.interactions.unfilterAll)
				a.chartConfig.interactions.unfilterAll();
			return;
		}
			
		a.chartConfig.data.map(function(d,i){
			if(!isNaN(data) && data == i ||
				isColor(data) && data == d.color ||
					typeof data == "string" && data == d.name){
				a.marked[i] = !a.marked[i];
				if(a.marked[i]){
					if(a.chartConfig.interactions.filter)
						a.chartConfig.interactions.filter(document.querySelector(".legend-"+i),d);
					a.g.select(".legend-"+i).select(".anchor").select(".muralpin").transition().duration(100).attr("opacity",1);
				}else{
					if(a.chartConfig.interactions.unfilter)
						a.chartConfig.interactions.unfilter(document.querySelector(".legend-"+i),d);
					a.g.select(".legend-"+i).select(".anchor").select(".muralpin").transition().duration(100).attr("opacity",0);
				}
			}
		})

		if(a.marked.indexOf(false)== -1 || a.marked.indexOf(true)== -1)
			this.setoption();
	}
	draw(){
		var a = this;
		this.define_disposition();
		var width = a.chartConfig.dimensions.right?(a.disposition[0].length*a.space):a.chartConfig.dimensions.width;
		this.width = width;
		var height = a.chartConfig.dimensions.right?a.chartConfig.dimensions.height:(a.chartConfig.layout.rect_size*(1+a.chartConfig.layout.padding)*this.disposition.length)
		this.svg.attr("width",width)
				.attr("height",height);

		this.axis.domain(range(this.disposition.length)).range([0,height]);
		if(a.g.selectAll(".row")._groups[0].length != this.disposition.length)
			this.row = a.g.selectAll(".row").remove();

		this.row = a.g.selectAll(".row").data(this.disposition).enter().append("g").attr("class","row")
			.attr("transform",function(d,i){return "translate("+(d.dx?a.space/2:0)+","+(a.axis(i)+(a.axis.bandwidth()-a.chartConfig.layout.rect_size)/2)+")"});

		this.legend = this.row.selectAll(".legend").data(function(d,i){return a.disposition[i]}).exit().remove();

		this.legend = this.row.selectAll(".legend").data(function(d,i){return a.disposition[i]}).enter().append("g")
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
			.transition().duration(500)
			.style("font-family",a.chartConfig.layout.font)
			.style("font-size",""+a.chartConfig.layout.font_size+"px")
			.style("font-style","normal")
			.style("font-weight","300")
			.style("line-height","normal")
			.attr("x",a.chartConfig.layout.rect_size*1.25)
			.attr("y",a.chartConfig.layout.rect_size*.25)
			.attr("dy",".6em")
			.text(function(d){return d.name});
		this.legend.select(".anchor").append("g").attr("class","muralpin")
			.attr("transform","translate("+a.chartConfig.layout.rect_size*.15+",0)").attr("opacity",0)
		if(!this.muralPinCreated)
			muralPin(this.legend.select(".anchor").select(".muralpin"),a.chartConfig.layout.rect_size,a.chartConfig.layout.rect_size,a.chartConfig.layout.stroke_over),this.muralPinCreated = true;
		else	
			muralPinRefatoring(this.legend.select(".anchor").select(".muralpin"),a.chartConfig.layout.rect_size,a.chartConfig.layout.rect_size,a.chartConfig.layout.stroke_over);

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
		
		

		this.g.attr("transform","translate("
			+(a.chartConfig.dimensions.right?(.25*a.chartConfig.layout.rect_size+a.chartConfig.dimensions.x):
				((a.chartConfig.dimensions.width-document.querySelector("#"+this.name+"-g").getBoundingClientRect().width)/2+a.chartConfig.dimensions.x))+","
			+(a.chartConfig.dimensions.y)+")");

			

		return this;
	}
	show_legend(){
		var a = this;
		if(a.chartConfig.dimensions.right)
			if(a.hide)
				a.svg
					.transition().duration(500)
					.attr("width",a.width),
				a.hide = false;
			else
				a.svg
					.transition().duration(500)
					.attr("width",a.chartConfig.layout.rect_size*1.5),
				a.hide = true;
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

		var max = 0;var max_height = 0;
		var legends = document.querySelector(a.chartConfig.target).querySelectorAll(".legend");
		for(var i=0;i<legends.length;i++){
			var temp = legends[i].getBoundingClientRect();
			a.chartConfig.data[i].width = temp.width;
			a.chartConfig.data[i].height = temp.height;
		}
		legends = a.chartConfig.data;
		
		for(var i=0;i<legends.length;i++){
			var temp = legends[i].width;
			max = max>temp?max:temp;
			temp = legends[i].height;
			max_height = max_height>temp?max_height:temp;
		}

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
					ret[ret.length-1].dx = true;
			}
			return ret;
		}

		function joinvector(vector){
			if(vector.length <=1){
				return vector;
			}
			var size = vector[0].length +1;
			for(var i=1;i<vector.length;i++){
				vector[0] = vector[0].concat(vector[i]);
			}
			var ret = vector[0].map(function(d){return [d]});
			var length = Math.floor(ret.length/size);
			var s = ret.length%size;
			for(var i=length-1;i>=0;i--){
				ret[i].concat(ret.pop(size+(i<s?1:0)));
			}
			return ret;
		}

		if(!a.chartConfig.dimensions.right){
			legends = [legends];
			this.space = max*1.4;
			var limit = max*1.1;
			var keep = true;
			var width = this.chartConfig.dimensions.width;
			while(keep){
				if(legends[0].length*this.space>width){
					if(width/legends[0].length >limit){
						this.space = width/legends[0].length;
						keep = false;
					}else{
						var temp = legends.length;
						legends = partvector(legends);
						if (temp == legends.length)
							keep = false;
					}
				}else{
					keep = false;
				}
			}
		}else{
			legends = legends.map(function(d){return [d]});
			this.space = a.chartConfig.dimensions.height/legends.length;
			var limit = max_height*(1+a.chartConfig.layout.padding);
			while(this.space< limit){
				legends = joinvector(legends);
				this.space = a.chartConfig.dimensions.height/legends.length;
				if(legends.length <=1)
					break;
			}

			this.space = max*1.1;
		}
		this.legend.remove();
		this.disposition = legends;
		return this;
	}
}