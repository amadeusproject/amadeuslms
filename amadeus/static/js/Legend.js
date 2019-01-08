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
    constructor(legendConfig){
	this.validData(legendConfig).create().draw().addInteractions();
    }
    validData(legendConfig){
	var a = this;
	if(legendConfig.data == undefined || legendConfig.data.name == undefined || legendConfig.data.color == undefined){
	    console.error("Impossible create legend without DataSource");
	    return;
	}
	if(legendConfig.data.name.length > legendConfig.data.color.length){
	    console.error("Impossible create legend with incompatible DataSource");
	    return;
	}
	if(legendConfig.parent == undefined){
	    console.error("Impossible create legend without SVG container");
	    return;
	}
	if(legendConfig.name == undefined){
	    legendConfig.name = "legend"+contLegend++;
	}
	
	if(legendConfig.font == undefined)legendConfig.font = {};
	if(legendConfig.font.name == undefined)legendConfig.font.name = "sans-serif";
	if(legendConfig.font.size == undefined)legendConfig.font.size = 15;
	if(legendConfig.font.align == undefined)legendConfig.font.align = "end";
	
	if(legendConfig.svg == undefined)legendConfig.svg = false;
	this.svg = legendConfig.svg?
		d3.select(legendConfig.parent):
		    d3.select(legendConfig.parent)
		    .append("svg")
		    .attr("id",legendConfig.name+"-container");
		
	if(legendConfig.position == undefined)legendConfig.position = {};
	if(legendConfig.position.align == undefined)legendConfig.position.align = "top-left";
	this.legendConfig = legendConfig;
	if(a.legendConfig.position.x != undefined)
	    a.legendConfig.position.xok = true;
	if(a.legendConfig.position.y != undefined)
	    a.legendConfig.position.yok = true;
	if(a.legendConfig.svg)
	    this.validXY();	
	
	legendConfig.interactions = d3.validEvents(legendConfig.interactions);
	
	return this;
    }
    create(){
	var a = this;
		
	this.g = this.svg.append("g").attr("id",this.legendConfig.name);
		
	this.ancor = this.g.append("g");
		
	this.background = this.ancor.append("rect")
		.attr("fill","#FFF");
	
	this.legendG = this.ancor.append("g").attr("id",a.legendConfig.name+"-inner").attr("font-family",this.legendConfig.font.name);
	
	this.legend = this.legendG.selectAll("g").data(this.legendConfig.data.name).enter()
		.append("g");
	this.legend.append("text").text(function(d) {
	    return d;
    	}).attr("dy", "0.85em");
	this.legend.append("rect").attr("fill", function(d,i){
	    return a.legendConfig.data.color[i]; 
	});
	return this;
    }
    draw(){
	var a = this;
	this.legendG.attr("font-size",this.legendConfig.font.size).attr("text-anchor", "start");
	
	this.background.attr("transform","translate(0,0)")
	.attr("width",0)
	.attr("height",0);
	
	this.legend.attr("transform", function(d, i) {
	    return "translate(0," + i * (a.legendConfig.font.size + 3) + ")";
	});
	
	this.legend.select("rect")
		.attr("width",this.legendConfig.font.size )
		.attr("height",this.legendConfig.font.size )
		.attr("x", -this.legendConfig.font.size-3);
	
	
	var legendDimensions = document.getDimensions("#"+this.legendConfig.name+"-inner");
	
	this.legendDimensions=legendDimensions;
	
	if(!a.legendConfig.svg){
	    this.svg
	    .attr("width",a.legendDimensions.w)
		.attr("height",a.legendDimensions.h)
	}
	
	this.validXY();
	
	this.g.attr("transform","translate("+this.legendConfig.position.x+","+this.legendConfig.position.y+")");
	
	var ancorConfig = this.legendConfig.position.align.split("-");
	this.legendG.attr("text-anchor", a.legendConfig.font.align);
	
	this.ancor.attr("transform",function(){
	    var x,y;
	    switch(ancorConfig[1]){
	    	case "center":x= -legendDimensions.w/2; break;//a.svg.attr("width")/2
	    	case "right":x= -legendDimensions.w; break;
	    	default:x= 0;break;
	    }
	    switch(ancorConfig[0]){
	    	case "middle":y= -legendDimensions.h/2; break;//a.svg.attr("height")/2
	    	case "bottom":y= -legendDimensions.h; break;
	    	default:y= 0; break;
	    }
	    return "translate("+x+","+y+")";
	    });
		
	this.legend.selectAll("text")
		.attr("x",function(){
		    switch(a.legendConfig.font.align){
		    	case "end":return a.legendDimensions.w-a.legendConfig.font.size-3;
			default: return a.legendConfig.font.size+3;
		    }
		});
			
	this.legend.selectAll("rect")
		.attr("x",function(){
		    switch(a.legendConfig.font.align){
		    	case "end":return a.legendDimensions.w-a.legendConfig.font.size;
			default: return 0;
		    }
		});
	
	this.background.attr("width",a.legendDimensions.w)
	.attr("height",a.legendDimensions.h).attr("transform","translate(0,0)");/**/
	
	
	
	return this;
    }
    validXY(){
	var a=this;
	var ancorConfig = a.legendConfig.position.align.split("-");
	if(!a.legendConfig.position.xok)
	    switch(ancorConfig[1]){
	    case "center":a.legendConfig.position.x = a.svg.attr("width")/2;break;
	    case "right":a.legendConfig.position.x = a.svg.attr("width");break;
	    default:a.legendConfig.position.x = 0;break;
	}
	    
	if(!a.legendConfig.position.yok)
	    switch(ancorConfig[0]){
	    	case "middle":a.legendConfig.position.y = a.svg.attr("height")/2;break;
	    	case "bottom":a.legendConfig.position.y = a.svg.attr("height");break;
	    	default:a.legendConfig.position.y = 0;break;
	}
	
	return this;
    }
    resize(val){
	this.legendConfig.font.size = val;
	return this.draw();
    }
    translate(x,y){
	if(x != undefined)
	    this.legendConfig.position.x = x;
	if(y != undefined)
	    this.legendConfig.position.y = y;
	return this.move();
    }
    move(x,y){
	if(x == undefined)
	    x = this.legendConfig.position.x;
	if(y == undefined)
	    y = this.legendConfig.position.y;
	this.g.transition().duration(500)
		.attr("transform","translate("+x+","+y+")");
	return this;
    }
    addInteractions(){
	var a = this;
	a.legendConfig.interactions.mouseout.push(function(element,data){
	    var currentEl = d3.select(element);
	    currentEl.attr("opacity",1);
	});
	a.legendConfig.interactions.mouseover.push(function(element,data){
	    var currentEl = d3.select(element);
	    currentEl.attr("opacity",0.5);
	});
	d3.addEvents(a.legend,a.legendConfig.interactions);
	     
	return this;
    }
}