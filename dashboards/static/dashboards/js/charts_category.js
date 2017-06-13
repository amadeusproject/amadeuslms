var charts = {
	line_chart: function(data, target_id){
		// 2. Use the margin convention practice 

	var margin = {top: 50, right: 50, bottom: 50, left: 50}
	  , width = 400 - margin.left - margin.right // Use the window's width 
	  , height = 400 - margin.top - margin.bottom; // Use the window's height

	var n = data.length;

	var xScale = d3.scaleTime().range([0, width]);

	var yScale = d3.scaleLinear().range([height, 0]);

	var line = d3.line()
    .x(function(d, i) { return xScale(d.date); }) // set the x values for the line generator
    .y(function(d) { return yScale(d.count); }) // set the y values for the line generator 
    .curve(d3.curveMonotoneX) // apply smoothing to the line

    var svg = d3.select("#left-chart").append("svg")
    	.attr("width", width)
    	.attr("height", height)
    	.append("g")
    	.attr("transform", "translate("+margin.left+","+margin.right+")");

    svg.append("g")
    	.attr("class", "y axis")
    	.call(d3.axisLeft(yScale));


    svg.append("path")
    	.datum(data)
    	.attr("class", "line")
    	.attr("d", line);

    svg.selectAll(".dot")
    	.data(data)
    	.enter().append("circle")
    	.attr('class', "dot")
    	.attr("cx",	 function(d,i ){
    		return xScale(i);
    	})
    	.attr("cy", function(d){
    		return yScale(d.count);
    	})
    	.attr("r", 5);
	},

};