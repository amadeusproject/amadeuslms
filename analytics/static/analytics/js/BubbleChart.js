/*var chartConfig = {
  name:"bubbleChartDashBoars",
  parent:target,
  data:data,
  dimensions:{
    width:490,
    height:400,
  },
  layout:{
    qtd:50,
    absForce:0.5,
  },
};*/
var bubbleChartCounter = 0;
class BubbleChart{
  constructor(chartConfig){    
    this.create(BubbleChart.validData(chartConfig)).draw();
  }
  static validData(chartConfig){
    if(chartConfig.data == undefined){
      console.error("Data setInvalid")
      throw new Exception();
    }
    if(chartConfig.name == undefined)chartConfig.name = "bubbleChart"+(bubbleChartCounter++);
    if(chartConfig.target == undefined)chartConfig.target = "body";
    
    if(chartConfig.dimensions == undefined)chartConfig.dimensions = {};
    if(chartConfig.dimensions.width == undefined)chartConfig.dimensions.width = 300;
    if(chartConfig.dimensions.height == undefined)chartConfig.dimensions.height = 300;

    if(chartConfig.layout == undefined)chartConfig.layout = {};
    if(chartConfig.layout.qtd == undefined)chartConfig.layout.qtd = 50;
    if(chartConfig.layout.absForce == undefined)chartConfig.layout.absForce = 0.5;

    chartConfig.interactions = d3.validEvents(chartConfig.interactions);

    if (chartConfig.tooltip != undefined) {//Configuration of tooltip
      //Without a text, this tooltip will not be created
      if (chartConfig.tooltip.text == undefined)
          chartConfig.tooltip = undefined;
      else {
          chartConfig.tooltip.name = chartConfig.name + "-toolTip";
          if (chartConfig.svg)
              chartConfig.tooltip.parent = chartConfig.parent;
          else
              chartConfig.tooltip.parent = "#" + chartConfig.name + "-container";
      }
  }

    return chartConfig;
  }
  create(chartConfig){
    var a = this;
    this.chartConfig = chartConfig;

    a.names = Array.removeRepetitions(a.chartConfig.data.map(function(d){return d.user_id;}));
    a.names = a.names.sort();
    
    a.data = a.names.map(function(d){return {user:d,value:0}});

    for(var i=0;i<a.chartConfig.data.length;i++){
      var index = a.names.indexOf(a.chartConfig.data[i].user_id);
      //if(a.chartConfig.data[index].gender==undefined)
        //a.chartConfig.data[index].gender = data[i].gender;
      if(a.data[index].image == undefined)  
        a.data[index].image = a.chartConfig.data[i].image;
      if(a.data[index].name == undefined)  
        a.data[index].name = a.chartConfig.data[i].user;
      a.data[index].value += a.chartConfig.data[i].value;
    }
    
    a.data = a.data.sort(function(d1,d2){return d1.value<d2.value?1:(d1.value>d2.value?-1:0);});
    //a.min = a.data[a.data.length-1].value;
    //a.max = a.data[0].value;

    this.a1 = 0;
    console.log(a.data);
    this.nodes = a.data.filter(
      function(d,i){
        if(i<a.chartConfig.layout.qtd){
          a.a1+=d.value;
          return true
        }
        return false 
      });
      
    a.nodes = a.nodes.map(function(i,j) {
      return {
        user:"user"+j,
        name:i.name,
        value:i.value,
        image:i.image
      };
    });
    console.log(a.nodes);

    this.svg = d3.select(a.chartConfig.parent).append("svg").attr("id",a.chartConfig.name+"-container");
    this.g = this.svg.append("g");

    this.bubbles = this.g.selectAll(".user-dot")
        .data(a.nodes)
      .enter().append("g")
        .attr("class","user-dot");

    return this;
  }
  draw(){
    var a = this;
    this.prop = Math.sqrt((a.chartConfig.dimensions.width-50)*(a.chartConfig.dimensions.height-50)/a.a1)/2.5;

    a.nodes = a.nodes.map(function(d){
      d.r = Math.round(Math.sqrt(d.value)*a.prop)
      
      return d;
    });

    var forcexy = function(abs,prop){
        return {x:Math.sqrt(abs*abs*prop/(prop+1)),
                y:Math.sqrt(abs*abs/(prop+1))}
    }

    var forceprop = function(x){
      return 2.287081443*Math.exp(-0.9045466968*x)
    }

    this.forces = forcexy(a.chartConfig.layout.absForce,forceprop(a.chartConfig.dimensions.width/a.chartConfig.dimensions.height));

    function constant(_) {
        return function () { return _ }
    }

    function boundedBox() {
        var nodes, sizes
        var bounds
        var size = constant([0, 0])

        function force() {
            var node, size
            var xi, x0, x1, yi, y0, y1
            var i = -1
            while (++i < nodes.length) {
                node = nodes[i]
                size = sizes[i]
                xi = node.x + node.vx
                x0 = bounds[0][0] - xi
                x1 = bounds[1][0] - (xi + size[0])
                yi = node.y + node.vy
                y0 = bounds[0][1] - yi
                y1 = bounds[1][1] - (yi + size[1])
                if (x0 > 0 || x1 < 0) {
                    node.x += node.vx
                    node.vx = -node.vx
                    if (node.vx < x0) { node.x += x0 - node.vx }
                    if (node.vx > x1) { node.x += x1 - node.vx }
                }
                if (y0 > 0 || y1 < 0) {
                    node.y += node.vy
                    node.vy = -node.vy
                    if (node.vy < y0) { node.vy += y0 - node.vy }
                    if (node.vy > y1) { node.vy += y1 - node.vy }
                }
            }
        }
        
        force.initialize = function (_) {
            sizes = (nodes = _).map(size)
        }

        force.bounds = function (_) {
            return (arguments.length ? (bounds = _, force) : bounds)
        }

        force.size = function (_) {
            return (arguments.length
                ? (size = typeof _ === 'function' ? _ : constant(_), force)
                : size)
        }

        return force
    }


    this.boxForce = boundedBox()
        .bounds([[0, 0], [a.chartConfig.dimensions.width, a.chartConfig.dimensions.height]])
        .size(function (d) { return [d.r*2, d.r*2] })

    function ticked() {
          var i = 0,
              n = a.nodes.length;
    
          a.svg.selectAll(".user-dot")
              .attr("transform",function(d){return "translate("+d.x+","+d.y+")"});
        };

    this.simulation = d3.forceSimulation(this.nodes)
        .velocityDecay(0.2)
        .force("x", d3.forceX().strength(this.forces.x))
        .force("y", d3.forceY().strength(this.forces.y))
        //.force('box', this.boxForce)
          .force("collide", d3.forceCollide().radius(function(d) { return d.r + 0.5; }).iterations(2))
          
        .on("tick", ticked);

    this.svg
        .attr("width", a.chartConfig.dimensions.width)
        .attr("height", a.chartConfig.dimensions.height);
    this.g
        .attr("transform","translate("+a.chartConfig.dimensions.width/2+","+a.chartConfig.dimensions.height/2+")")
        .attr("id","bubbleChart");

    this.svg.append("defs")
      .append("linearGradient")
        .attr("id","svgGradient")
        .attr("x1","0%").attr("x2","100%")
        .attr("y1","0%").attr("y2","100%")
        .selectAll("stop").data([{class:"start",offset:"0%",stop_color:"#007991",stop_opacity:"1"},
        {class:"end",offset:"100%",stop_color:"#78ffd6",stop_opacity:"1"}])
        .enter().append("stop")
          .attr("class",function(d){return d.class})
          .attr("offset",function(d){return d.offset})
          .attr("stop-color",function(d){return d.stop_color})
          .attr("stop-opacity",function(d){return d.stop_opacity});
    this.svg.select("defs")
      .selectAll("pattern").data(a.nodes).enter()
      .append("pattern")
        .attr("id",function(d,i){return d.user})
        .attr("width",function(d){return d.r})
        .attr("height",function(d){return d.r})
        .append("image")
          .attr("xlink:href",function(d,i){//return d.gender=="m"?imageM[i%imageW.length]:imageW[i%imageW.length]
            return d.image;
        })
          .attr("width",function(d){return 2*d.r})
          .attr("height",function(d){return 2*d.r})
          .attr("x",0)
          .attr("y",0)
    this.bubbles//.selectAll(".img")
      .append("circle").attr("class","img")
        
        //.attr("stroke","url(#svgGradient)")
        .attr("r", function(d) { return d.r; })
        //.attr("fill", function(d, i) { return color[d.gender=="m"?0:1]; })
        //.attr("stroke","url(#svgGradient)")//
        //.attr("stroke-width",1);
        
    this.bubbles//.selectAll("temp")
      .append("circle").attr("class","temp")
        .attr("r", function(d) { return d.r; })
        .attr("stroke","url(#svgGradient)")
        .attr("fill", "#007991")
        .attr("stroke-width",1)
        .attr("opacity",1);

    this.bubbles.select(".img").transition().delay(function(d,i){return 900*Math.sqrt(i)})
      .attr("fill",function(d){return "url(#"+d.user+")"})
    this.bubbles.select(".temp").transition().delay(function(d,i){return 910*Math.sqrt(i)}).duration(500)
      .attr("opacity",0);
    this.bubbles.select(".temp").transition().delay(function(d,i){return 910*Math.sqrt(i)+510})
      .remove();

    //Construct tooltip
    this.toolTipConstruct();
    this.addInteractions();

    return this;
  }
  toolTipConstruct() {//Construct and configurate toltip
    var a = this;
    if(this.toolTip == undefined)
    if (this.chartConfig.tooltip != undefined) {
        this.toolTip = new ToolTip(this.chartConfig.tooltip);
        a.chartConfig.interactions.mouseover.push(function (element, data) {
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
    if(a.interactionsAdded)
      return;

    a.interactionsAdded = true;
    a.chartConfig.interactions.mouseover.push(function (element, data) {
        var currentEl = d3.select(element).select("rect");
        currentEl.attr("opacity", 0.8);        
    });
    a.chartConfig.interactions.mouseout.push(function (element, data) {
        var currentEl = d3.select(element).select("rect");
        currentEl.attr("opacity", 1);
    });

    d3.addEvents(a.bubbles, a.chartConfig.interactions);

    return this;
}
}

/*function bubble(data,target){
var width = 490,
    height = 400,
    tau = 2 * Math.PI,
    qtd = 50;

  var chartConfig = {
      name:"bubbleChartDashBoars",
      parent:target,
      data:data,
      dimensions:{
        width:490,
        height:400,
      },
      layout:{
        qtd:50,
        absForce:0.5,
      },
    };
console.log(data.length);
names = Array.removeRepetitions(data.map(function(d){return d.user_id;}));
names = names.sort();
var dataTemp = data
data = names.map(function(d){return {user:d,value:0}});
for(var i=0;i<dataTemp.length;i++){
  var index = names.indexOf(dataTemp[i].user_id);
  //if(chartConfig.data[index].gender==undefined)
    //chartConfig.data[index].gender = data[i].gender;
  if(data[index].image == undefined)  
    data[index].image = dataTemp[i].image;
  data[index].value += dataTemp[i].value;
}

data = data.sort(function(d1,d2){return d1.value<d2.value?1:(d1.value>d2.value?-1:0);});
var min = data[data.length-1].value;
var max = data[0].value;


var a1 = 0;

var nodes = data.filter(function(d,i){if(i<qtd){a1+=d.value;return true}return false });
var prop = Math.sqrt((width-50)*(height-50)/a1)/2.5;

nodes = nodes.map(function(i,j) {
  return {
    r: Math.round(Math.sqrt(i.value)*prop),
    //r:j,
    user:"user"+j,
    //name:i.user,
    value:i.value,
    image:i.image
  };
});
console.log(nodes)

var color = ["#1164D8","#E56485"];
//var imageW = ["image1.jpg","image2.jpg","image3.jpg","image4.jpg","image5.jpg","image6.jpg","image7.jpg",]
//var imageM = ["image8.jpg","image9.jpg","image10.jpg","image11.jpg","image12.jpg","image13.jpg","image14.jpg",]

var abs = .04;

var forcexy = function(abs,prop){
    return {x:Math.sqrt(abs*abs*prop/(prop+1)),
            y:Math.sqrt(abs*abs/(prop+1))}
}

var forceprop = function(x){
  return 2.287081443*Math.exp(-0.9045466968*x)
}

var forces = forcexy(abs,forceprop(width/height));

function constant(_) {
    return function () { return _ }
}

function boundedBox() {
    var nodes, sizes
    var bounds
    var size = constant([0, 0])

    function force() {
        var node, size
        var xi, x0, x1, yi, y0, y1
        var i = -1
        while (++i < nodes.length) {
            node = nodes[i]
            size = sizes[i]
            xi = node.x + node.vx
            x0 = bounds[0][0] - xi
            x1 = bounds[1][0] - (xi + size[0])
            yi = node.y + node.vy
            y0 = bounds[0][1] - yi
            y1 = bounds[1][1] - (yi + size[1])
            if (x0 > 0 || x1 < 0) {
                node.x += node.vx
                node.vx = -node.vx
                if (node.vx < x0) { node.x += x0 - node.vx }
                if (node.vx > x1) { node.x += x1 - node.vx }
            }
            if (y0 > 0 || y1 < 0) {
                node.y += node.vy
                node.vy = -node.vy
                if (node.vy < y0) { node.vy += y0 - node.vy }
                if (node.vy > y1) { node.vy += y1 - node.vy }
            }
        }
    }
    
    force.initialize = function (_) {
        sizes = (nodes = _).map(size)
    }

    force.bounds = function (_) {
        return (arguments.length ? (bounds = _, force) : bounds)
    }

    force.size = function (_) {
        return (arguments.length
             ? (size = typeof _ === 'function' ? _ : constant(_), force)
             : size)
    }

    return force
}


var boxForce = boundedBox()
    .bounds([[0, 0], [width, height]])
    .size(function (d) { return [d.r*2, d.r*2] })

var simulation = d3.forceSimulation(nodes)
    .velocityDecay(0.2)
    .force("x", d3.forceX().strength(forces.x))
    .force("y", d3.forceY().strength(forces.y))
    //.force('box', boxForce)
      .force("collide", d3.forceCollide().radius(function(d) { return d.r + 0.5; }).iterations(2))
      
    .on("tick", ticked);

var svg = d3.select(target).append("svg")
    .attr("width", width)
    .attr("height", height);
var g = svg.append("g")
    .attr("transform","translate("+width/2+","+height/2+")")
    .attr("id","bubbleChart");
var bubbles = g.selectAll(".user-dot")
    .data(nodes)
  .enter().append("g")
    .attr("class","user-dot");

svg.append("defs")
  .append("linearGradient")
    .attr("id","svgGradient")
    .attr("x1","0%").attr("x2","100%")
    .attr("y1","0%").attr("y2","100%")
    .selectAll("stop").data([{class:"start",offset:"0%",stop_color:"#007991",stop_opacity:"1"},
    {class:"end",offset:"100%",stop_color:"#78ffd6",stop_opacity:"1"}])
    .enter().append("stop")
      .attr("class",function(d){return d.class})
      .attr("offset",function(d){return d.offset})
      .attr("stop-color",function(d){return d.stop_color})
      .attr("stop-opacity",function(d){return d.stop_opacity});
svg.select("defs")
  .selectAll("pattern").data(nodes).enter()
  .append("pattern")
    .attr("id",function(d,i){return d.user})
    .attr("width",function(d){return d.r})
    .attr("height",function(d){return d.r})
    .append("image")
      .attr("xlink:href",function(d,i){//return d.gender=="m"?imageM[i%imageW.length]:imageW[i%imageW.length]
        return d.image;
    })
      .attr("width",function(d){return 2*d.r})
      .attr("height",function(d){return 2*d.r})
      .attr("x",0)
      .attr("y",0)
bubbles
  .append("circle").attr("class","img")
    //.attr("r",function(d){return d.r})
    
    //.attr("stroke","url(#svgGradient)")
    .attr("r", function(d) { return d.r; })
    .attr("fill", function(d, i) { return color[d.gender=="m"?0:1]; })
    //.attr("stroke","url(#svgGradient)")
    .attr("stroke-width",1);
    
bubbles
  .append("circle").attr("class","temp")
    .attr("r", function(d) { return d.r; })
    .attr("stroke","url(#svgGradient)")
    .attr("fill", "#007991")
    .attr("stroke-width",1)
    .attr("opacity",1);
    

function ticked() {
  var i = 0,
      n = nodes.length;

  svg.selectAll(".user-dot")
      .attr("transform",function(d){return "translate("+d.x+","+d.y+")"});
};

bubbles.select(".img").transition().delay(function(d,i){return 900*Math.sqrt(i)})
  .attr("fill",function(d){return "url(#"+d.user+")"})
bubbles.select(".temp").transition().delay(function(d,i){return 910*Math.sqrt(i)}).duration(500)
  .attr("opacity",0);
bubbles.select(".temp").transition().delay(function(d,i){return 910*Math.sqrt(i)+510})
  .remove();
  
}*/