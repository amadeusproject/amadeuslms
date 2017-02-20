/*
	HOME CHARTS
*/

//Adding this code by @jshanley to create a filter to look for the last child

d3.selection.prototype.first = function() {
  return d3.select(this[0]);
};
d3.selection.prototype.last = function() {
  var last = this.size() - 1;
  return d3.select(this[last]);
};

var resource_donut_chart = {
	build: function(url){
		$.get(url, function(dataset){
			

	        var width = 600;
	        var height = 480;
	        var padding = 30;
	        var radius = Math.min(width, height) / 2 - padding;
	       
	        var color = d3.scaleOrdinal(d3.schemeCategory20c);
	        var new_div = d3.select(".carousel-inner").append("div").attr("class","item");
	        var svg = new_div.append("svg").attr("width", width).attr("height", height)
	        	.style("margin","auto")
	        	.style("display","block")
	        	.append('g')
	          	.attr('transform', 'translate(' + (width / 2) +
	            ',' + (height / 2 ) + ')');
	      
	     

	        var donutInner = 50;
	        var arc = d3.arc()
	          .innerRadius(radius - donutInner)
	          .outerRadius(radius);

	        svg.append("text")
	        	.attr("text-anchor", "middle")
	        	.attr("x",0  )
	        	.attr("y", -height/2 + padding)  
	        	.style("font-size", "30px") 
	        	.text("Recursos mais utilizados");


	        var pie = d3.pie()
	          .value(function(d) { return d[1]; })
	          .sort(null);

	        

	        var path = svg.selectAll('path')
	          .data(pie(dataset))
	          .enter()
	          .append('path')
	          .attr('d', arc)
	          .attr('fill', function(d, i) {
	            return color(i);
	          });
	        
	       	
	       	svg.selectAll("text.pie-tooltip")
            .data(dataset)
            .enter()
            .append("text")
                    .text(function(d){
                        return d[0];
                    })
                    .attr("id", function(d){
                    	return d[0];
                    })
                    .attr("class","pie-tooltip");

            path.on('mouseover', function(d) { //When the mouse is over the path         
			  $('#'+d.data[0]).css("display", "block");                                   
			});                                          

			path.on('mouseout', function(d) { //When the mouse "leaves" the path
			  t = $('#'+d.data[0]).css("display", "none");                                   
			});                                          

		}) // end of the get method
	}
}

resource_donut_chart.build('/topics/count_resources/');