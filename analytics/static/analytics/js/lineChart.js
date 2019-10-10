var lineChartConut = 0;

var chartConfig = {
    data:{
        func:function(x){
            return x;
        },
        interval:[0,100],
        divisions:100
    },
    name:"LineChart1",
    target:"body",
    dimensions:{
        width:800, height:600
    },
    margin:{top:10,bottom:20,left:20,right:10},
    layout:{
        stroke:"#00f",
        stroke_width:2,
        back_color:"#eee",
    }
}

class LineChart{
    constructor(chartConfig){
        this.create(LineChart.validChart(chartConfig));
    }
    static validChart(chartConfig){
        return chartConfig;
    }
    create(chartConfig){
        var a = this;
        this.chartConfig = chartConfig;
        this.svg = d3.select(this.chartConfig.target).append("svg").attr("id",a.chartConfig.name);
        this.g = this.svg.append("g");

        this.get_points();

        this.x = d3.scaleLinear().domain([0,1]);
        this.y = d3.scaleLinear().domain([0,this.max]);

        this.lineFunction = d3.line()
            .x(function(d){
                return a.x(d)
            })
            .y(function(d){
                return a.y(d)
            })

        this.xAxis = this.g.append("g");

        this.yAxis = this.g.append("g");

        this.line = this.g.append("path");

    }
    draw(){
        var a = this;

        this.width = a.chartConfig.dimensions.width - a.chartConfig.margin.left - a.chartConfig.margin.right;
        this.height = a.chartConfig.dimensions.height - a.chartConfig.margin.top - a.chartConfig.margin.bottom;

        this.x.range([0,this.width]);
        this.y.range([this.height,0]);

        this.svg
            .attr("width",a.chartConfig.dimensions.width)
            .attr("height",a.chartConfig.dimensions.height);
        
        this.g 
            .attr("transform","translate("+a.chartConfig.margin.left+","+a.chartConfig.margin.top+")");
        
        
        

        
        return this;
    }
    get_points(){
        var band = 1/this.chartConfig.data.divisions;
        var ret = [];
        var f = this.chartConfig.data.func;
        this.max = f(0);

        for(var i = 0; i<=this.chartConfig.data.divisions;i++){
            var temp = f(i*band);
            ret.push({x:i*band,y:temp})
            this.max = this.max>temp?max:temp;
        }
        this.points = ret;
        return this;
    }
}