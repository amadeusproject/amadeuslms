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

var charts = {
	build_resource: function(url){
		$.get(url, function(dataset){
			

	        var width = 600;
	        var height = 300;
	        var padding = 30;
	        var radius = Math.min(width, height) / 2 - padding;
	       
	        var color = d3.scaleOrdinal(d3.schemeCategory20);
	        var new_div = d3.select(".carousel-inner").append("div").attr("class","item");
	        var svg = new_div.append("svg").attr("width", width).attr("height", height)
	        	.style("margin","auto")
	        	.style("display","block")
	        	.append('g')
	          	.attr('transform', 'translate(' + (width / 2) +
	            ',' + (height / 2 + padding ) + ')');
	      
	     

	        var donutInner = 50;
	        var arc = d3.arc()
	          .innerRadius(radius - donutInner)
	          .outerRadius(radius);

	        svg.append("text")
	        	.attr("text-anchor", "middle")
	        	.attr("x",0  )
	        	.attr("y", -height/2 )  
	        	.style("font-size", "30px") 
	        	.text("Recursos mais utilizados")
	        	.attr("fill", "#003333")
	        	.style("font-weight", "bold")
	        	.style("font-style", "italic");


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
	        var labelArc = d3.arc()
			    .outerRadius(radius*1.2 - donutInner)
			    .innerRadius(radius*1.2 - donutInner);

	       	
	       	svg.selectAll("text.pie-tooltip")
            .data(pie(dataset))
            .enter()
            .append("text")
                    .attr("id", function(d){
                    	return d.data[0];
                    })
                    .attr("class","pie-tooltip")
                    .attr('fill',"#172121")
                    .attr("transform", function(d) { return "translate(" + labelArc.centroid(d) + ")"; })
				      .attr("dy", ".35em")
				      .text(function(d) { return d.data[0]; });

                                

		}) // end of the get method
	},

	build_bubble_user: function(url){
		$.get(url, function(dataset){
			var width = 600;
	        var height = 300;
	       
	        
	       	function min(){
	       		min = 100000000000;
	       		for(var i = 0; i < dataset.length; i++){
	       			if (dataset[i]['count'] < min){
	       				min = dataset[i]['count'];
	       			}
	       		}

	       		return min
	       	}

	       	function max(){
	       		max = 0;
	       		for(var i = 0; i < dataset.length; i++){
	       			if (dataset[i]['count'] > max){
	       				max = dataset[i]['count'];
	       			}
	       		}

	       		return max
	       	}
	       	


	        var color = d3.scaleOrdinal(d3.schemeCategory20);
	         //adding new div to carousel-inner div
	        var new_div = d3.select(".carousel-inner").append("div").attr("class","item"); 
	        var radiusScale = d3.scaleSqrt().domain([min(), max()]).range([10,50]);
	        var svg = new_div.append("svg").attr("width", width).attr("height", height)
	        	.style("margin","auto")
	        	.style("display","block")
	        	.append('g')
	        	.attr("transform", "translate(0,0)")
	        	.attr("width", width)
	        	.attr("height", height);

	        //adding svg title

	        svg.append("text")
	        	.attr("text-anchor", "middle")
	        	.attr("x", width/2  )
	        	.attr("y", 30)  
	        	.style("font-size", "30px") 
	        	.text("Usuários mais ativos no Amadeus")
	        	.attr("fill", "#003333")
	        	.style("font-weight", "bold")
	        	.style("font-style", "italic");

	        var simulation = d3.forceSimulation()
	        	.force("x", d3.forceX(width/2).strength(0.05))
	        	.force("y", d3.forceY(height/2).strength(0.05))
	        	.force("collide", d3.forceCollide(function(d){
	        		return radiusScale(d['count']);
	        	}));

	        //First I create as many groups as datapoints so 
	        //it can hold all other objects (circle, texts, images)
	        var groups = svg.selectAll('.users-item')
	        	.data(dataset)
	        	.enter()
	        	.append("g")
	        	.attr("class",".user-dot");

	       	//Create circles to be drawn
	       	var circles = groups
	       		.append('circle')
	       		.attr("r", function(d){
	       			return radiusScale(d['count']);
	       		})

	       		.attr("fill", function(d){
	       			//return color(d['count']);
	       			return 'url('+'#'+'user_'+d['user_id']+')';
	       		});



	       	//Add texts to show user names
	       	groups.append("text")
	       	.text(function(d){
	       		return d['user'];
	       	}).attr("fill", "#FFFFFF")
	       	.attr("id", function(d){
	       		return "user_tooltip_"+d['user_id'];
	       	}).style("display", "none");


	       	groups.on("mouseover", function(d){
	       		$("#"+"user_tooltip_"+d['user_id']).show();
	       	});


	       	groups.on("mouseout", function(d){
	       		$("#"+"user_tooltip_"+d['user_id']).hide();
	       	});

	       	var defs = groups.append('svg:defs');

			defs.append("svg:pattern")
			    .attr("id", function(d){
			    	return "user_"+d['user_id'];
			    })
			    .attr("width", function(d){
	       			return radiusScale(d['count']);
	       		})
			    .attr("height", function(d){
	       			return radiusScale(d['count']);
	       		})
			    .append("svg:image")
			    .attr("xlink:href", function(d){
			    	return d['image'];
			    })
			    .attr("width",function(d){
	       			return radiusScale(d['count'])*2;
	       		})
			    .attr("height", function(d){
	       			return radiusScale(d['count'])*2;
	       		})
			    .attr("x", 0)
			    .attr("y", 0);



	       	//simulation
	       	simulation.nodes(dataset)
	       		.on('tick', ticked); //so all data points are attached to it

	       	function ticked(){
	       		groups.attr("transform", function(d){
	       			return "translate(" + d.x + "," + d.y + ")";
	       		})
	       	}
		});


	}
}

charts.build_resource('/topics/count_resources/');
charts.build_bubble_user('/users/get_users_log/');