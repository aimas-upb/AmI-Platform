define ['cs!widget'], (Widget) ->
    
    class ArduinoWidget extends Widget
        
        template_name: 'templates/arduino.hjs'
        subscribed_channels: ['/temperature_1']
        
        COLD_TEMP = 15
        MEDIUM_TEMP = 25
        WARNING_TEMP = 30
        HOT_TEMP = 35
        CENTER_X = 100
        CENTER_Y = 100
        
        
        
        initialize: =>
            @renderLayout()
            @svg = d3.select("#arduino_temperature")
                .append("svg")
            @svg.attr("width",500)
                .attr("height", 500)
            @circle= @svg.append("circle")
            @name = @svg.append("text")
            @value = @svg.append("text")
            
            @color_scale = d3.scale.linear().domain([COLD_TEMP, MEDIUM_TEMP , WARNING_TEMP, HOT_TEMP])
                .range(["blue", "green", "yellow", "red"])
                .clamp(true)
            #@circle = @svg.selectAll("circle")
            @circle.attr("cx", CENTER_X)
                .attr("cy", CENTER_Y)
                .attr("r", 75)
                .attr("fill", @color_scale(MEDIUM_TEMP))
            
            @value.attr("x", CENTER_X)
                .attr("y", CENTER_Y)
                .attr("font-size", "30px")
                .attr("fill", "black")
                .attr("text-anchor", "middle")
            
            @name.attr("x", CENTER_X)
                .attr("y", () -> CENTER_Y  - 75)
                .attr("font-size", "30px")
                .attr("fill", "black")
                .attr("text-anchor", "middle")
            

        
        get_temperature_1: (params) =>
            return unless params.model != null
            vals = params.model.get("measurement")
            #document.getElementById('arduino_temperature').innerHTML = vals;
            @circle.data([vals])
            @circle.transition()
                    .delay(250)
                    .duration(1500)
                    .attr("fill", @color_scale(vals))
            @value.data([vals])
                .text((d) -> d)
            return
            #circle.enter()
             #   .attr()
            
            #return unless params.type == "change"
            