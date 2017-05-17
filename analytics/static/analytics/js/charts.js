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
	      
	     

	        var donutInner = 20;
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
			    .outerRadius(radius - donutInner + 30)
			    .innerRadius(radius + 20 );

	       	//Adding tooltips to each part of the pie chart.
	       	svg.selectAll("text.pie-tooltip")
            .data(pie(dataset))
            .enter()
            .append("text")
                    .attr("id", function(d){
                    	return d.data[0];
                    })
                    .attr("class","pie-tooltip")
                    .attr('fill',"#172121")
                    .attr("transform", function(d) { 
                    	c = labelArc.centroid(d);
                    	return "translate(" + (c[0]*1.0 - 20) +"," + c[1]*0.8 + ")"; 
                    })
				      .attr("dy", ".25em")
				      .text(function(d) { return d.data[0] +'('+ d.data[1] +')'; });

                                

		}) // end of the get method
	},

	build_bubble_user: function(url){
		$.get(url, function(dataset){
			var width = 300;
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
	        var new_div = d3.select(".middle-chart").append("div").attr("class","item"); 
	        var radiusScale = d3.scaleSqrt().domain([min(), max()]).range([10,50]);
	        var svg = new_div.append("svg").attr("width", width).attr("height", height)
	        	.style("margin","auto")
	        	.style("display","block")
	        	.append('g')
	        	.attr("transform", "translate(0,0)")
	        	.attr("width", width)
	        	.attr("height", height);

	        

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


	       	var defs = groups.append('svg:defs');

	        var gradient = defs.append("linearGradient")
			   .attr("id", "svgGradient")
			   .attr("x1", "0%")
			   .attr("x2", "100%")
			   .attr("y1", "0%")
			   .attr("y2", "100%");

			gradient.append("stop")
			   .attr('class', 'start')
			   .attr("offset", "0%")
			   .attr("stop-color", "#007991")
			   .attr("stop-opacity", 1);

			gradient.append("stop")
			   .attr('class', 'end')
			   .attr("offset", "100%")
			   .attr("stop-color", "#78ffd6")
			   .attr("stop-opacity", 1);


	       	//Create circles to be drawn
	       	var circles = groups
	       		.append('circle')
	       		.attr("r", function(d){
	       			return radiusScale(d['count']);
	       		})

	       		.attr("fill", function(d){
	       			return 'url('+'#'+'user_'+d['user_id']+')';
	       		})
	       		.attr("stroke", "url(#svgGradient)") //using id setted by the svg
	       		.attr("stroke-width", 3);



	       	//Add texts to show user names
	       	/*groups.append("text")
	       	.text(function(d){
	       		return d['user'] +'('+ d['count'] + ')';
	       	}).attr("fill", "#000000")
	       	.attr("id", function(d){
	       		return "user_tooltip_"+d['user_id'];
	       	}).style("display", "none");*/

	       	var tooltip_div = d3.select("body").append("div")
	       		.attr('class','user-tooltip')
	       		.attr("display", "none")
	       		.attr("height", 28)
	       		.attr("width", 80)
	       		.style("position", "absolute")
	       		.style('pointer-events', 'none');




	       	groups.on("mouseover", function(d){
	       		//$("#"+"user_tooltip_"+d['user_id']).show();
	       		tooltip_div.transition().duration(500).style("opacity", .9);
	       		tooltip_div.html(d['user'] + '</br>' +  d['count'] + ' acessos')
	       		.style("left", (d3.event.pageX) + "px")
	       		.style("top", (d3.event.pageY - 28) + "px");
	       	});


	       	groups.on("mouseout", function(d){
	       		//$("#"+"user_tooltip_"+d['user_id']).hide();
	       		tooltip_div.transition().duration(500).style("opacity", 0);
	       		
	       	});


	       	//Attching images to bubbles
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


	},

	most_accessed_subjects: function(url){
		$.get(url, function(dataset){
			var width = 200;
            var height = 300;

            var new_div = d3.select(".carousel-inner").append("div").attr("test","ok");

           	var svg = new_div.append("svg").attr("width", "100%").attr("height", height)
	        	.style("margin","auto")
	        	.style("display","block");

	        var barPadding = 2
	        var bottomPadding = 15;
	        var marginLeft = 170; //Margin Left for all bars inside the graph
	      	
	      	var yScale = d3.scaleLinear()
                     .domain([0, d3.max(dataset, function(d) { return d.count; })])
                     .range([bottomPadding, 260]);

		    var rects = svg.selectAll("rect")
	        .data(dataset)
	        .enter()
	        	.append("g");
	            
	        rects.append("rect")
	            .attr("x", function(d, i){
	                return i * (width / dataset.length ) + barPadding + marginLeft ;
	            })
	            .attr("y", function(d){
	                return height - yScale(d.count) - bottomPadding;
	            })
	            .attr("width", 
	            	width / dataset.length - barPadding
	            )
	            .attr("height", function(d){
	                return  yScale(d.count);
	            });


	        var tooltipDiv = new_div.append("div").attr("class","bar-tip");

         	rects.on("mouseover", function(d, i){
	       		$(this).attr("fill", "red");
	       		$("#accessed_subject_"+i).show(); //So the tooltip is hidden 
	       		 tooltipDiv.transition()		
                .duration(200)		
                .style("opacity", .9);		
            	tooltipDiv.html("<p style='font-size:9px'>" + d.name + "( " + d.count + " )" +"</p>")	
                .style("left", (i * (width / dataset.length ) + barPadding + marginLeft) + "px")		
                .style("top", (height - yScale(d.count) - bottomPadding) + "px");
	       	});

	       	rects.on("mouseout", function(d, i ){
	       		$(this).attr("fill", "black");
	       		
	       		$("#accessed_subject_"+i).hide(); //So the tooltip shows up


	       		  tooltipDiv.transition()		
                .duration(500)		
                .style("opacity", 0);	
	       			
	       	});

	     

	        //Styling title
	       	 svg.append("text")
		        .attr("x", width/2)             
		        .attr("y", 30)
		        .attr("text-anchor", "middle")  
		        .style("font-size", "30px") 
		        .text("Subjects mais acessados")
		         .attr("fill", "#003333")
	        	.style("font-weight", "bold")
	        	.style("font-style", "italic");

		});
	},
	most_used_tags: function(url){
		$.get(url, function(dataset){
			//get most used tags across all amadeus
			var width = 800;
			var height = 300;

			
	       	

			var container_div = d3.select("#most-used-tags-body");
			if($('#most_used_tag_chart').length > 0){
				$('#most_used_tag_chart').remove();
			}

			var svg = container_div.append("svg").attr("width", "100%").attr("height", height)
			.attr("id", "most_used_tag_chart")
			.style("margin","auto")
	        	.style("display","block")
	        	.style("background","#ddf8e7")
	        	.append('g')
	        	.attr("transform", "translate(0,0)")
	        	.attr("width", "100%")
	        	.attr("height", height - 60);

	        
	        var color = d3.scaleLinear()
	     	.domain([0,1,2])
	     	.range(['#bdbdbd','#52b7bd', '#149e91']);
	     	//this function is to support the mapping for possible colors
	     	function getRandomInt(min, max) {
			  min = Math.ceil(min);
			  max = Math.floor(max);
			  return Math.floor(Math.random() * (max - min)) + min;
			}

	        var xScale = d3.scaleSqrt().domain([d3.min(dataset, function(d){ return d['count']}), 
	        	d3.max(dataset, function(d){ return d.count; })]).range([100,200]);
	        var tag_cloud = svg.selectAll('.tag-cloud-div')
	        .data(dataset)
	        .enter()
	        .append('g')
	        .attr("class", "data-container");


	        var tag_rects = tag_cloud
	        .append('rect')
	        .attr('class', 'tag-cloud')
	        .attr("width", function(d){
	        	return xScale(d['count'])*1.2;
	        })
	        .attr("height", function(d){
	        	return xScale(d["count"])*0.4;
	        })
	        .attr("fill", function(d, i) {
	            return color(getRandomInt(0,3));
	          })
	        .attr("rx", 20)
	        .attr("ry", 20);

	        var tag_texts = tag_cloud
	        .append("text")
	       	.text(function(d){
	       		return d['name'];
	       	})
	       	.attr("text-anchor", "middle")
	       	.attr("x", function(d){
	       		return xScale(d['count'])*1.2/2;
	       	})
	       	.attr("y", function(d){
	       		return xScale(d["count"])*0.4/2;
	       	})
	       	.attr("class", "tag-name")
	       	.attr("fill", "#ffffff")
	       	.style("font-size", function(d){
	       		return xScale(d["count"])*0.1 + "px";
	       	});


		    var simulation = d3.forceSimulation()
		        .force("x", d3.forceX(width/2).strength(0.05))
		        .force("y", d3.forceY(height/2).strength(0.05))
		        .force("charge", d3.forceManyBody().strength(-120).distanceMax(300)
                   .distanceMin(0));
		    /*
		      .force("collide", d3.forceCollide(function(d){
		        	return xScale(d['count'])*0.3;
		        }))*/
		    //simulation
	       	simulation.nodes(dataset)
	       		.on('tick', ticked); //so all data points are attached to it

	       	function ticked(){
	       		tag_cloud.attr("transform", function(d){
	       			return "translate(" + d.x + "," + d.y + ")";
	       		})
	       	}

		});
	},
	month_heatmap: function(data, target, div_target){

		
		
		
		if($('#'+div_target).lenght != 0 ){
			$('#'+div_target).fadeOut();
			$('#'+div_target).remove();
		}
		var width = 300;
		var height = 200;
		var svg = d3.select(target).append('svg')
		.attr('width', width)
		.attr('height', height);
		
		svg.attr('id', div_target);
	

		//color range
		var color = d3.scaleLinear().range(["#29c8b8", '#149e91']).domain([0, d3.max(data, function(d){ return d.count; })]);

	    var rects = svg.selectAll("rect")
	        .data(data)
	        .enter()
	        	.append("g");
	    rect_width = 40;
	    rect_height = 40;        
	    rects.append("rect")
	    	.attr("width", rect_width)
	    	.attr("height", rect_height)
	    	.attr("class", "day_rect")
	    	.attr("x", function(d, i){

	    		return rect_width* (i % 7);
	    	}).attr("y", function(d, i){
	    		return rect_height*(Math.floor(i / 7));
	    	}).attr("fill", function(d, i ){
	    		return color(d.count);
	    	});

	    rects.append("text")
	    	.text( function(d){
	    		return d.day;
	    	}).attr("fill", "white")
	    	.attr("text-anchor", "middle")
	    	.attr("x", function(d, i){
	    		return rect_width* ( i % 7) + rect_width/2;
	    	}).attr("y", function(d, i){
	    		return rect_height*(Math.floor(  i  / 7)) + rect_height/2;
	    	});

	    rects.on('mouseover', function(d, i){
	    	tooltip = d3.select(target)
	    		.append('div')
	    		.attr('class', 'date-tooltip')
	    		.style("left", ((d3.event.pageX) - width/2) + "px")
	    		.style("top", ((d3.event.pageY) - height/2) + "px")
	    		.style("position", "absolute")
	    		.html(d['count'])
	    });

	    rects.on('mouseout', function(){
	    	tooltip.remove();
	    })
	}
}


$(document).ready(function(){
	
	//charts.most_accessed_subjects('/subjects/most_accessed_subjects');
});
