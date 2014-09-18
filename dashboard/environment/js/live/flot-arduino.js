//Flot Line Chart
var offset = 0;
var dayOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thr", "Fri", "Sat"];
var DECAY = 7200000

function plotChart(series, sensorsIds, chartId) {
    // series
    var options = {
        series: {
            lines: {
                show: true
            },
            points: {
                show: false
            }
        },
        grid: {
            hoverable: true //IMPORTANT! this is needed for tooltip to work
        },
        // yaxis: {
        //     min: 27,
        //     max: 29
        // },
        xaxis:{
            mode: "time",
            tickFormatter: function (val, axis) {           
                // return dayOfWeek[new Date(val).getDay()];
                var myDate = new Date(val);
                return myDate;
            }
        },
        tooltip: true,
        tooltipOpts: {
            content: "'%s' of %x.2 is %y.02",
            shifts: {
                x: -60,
                y: 25
            }
        },
        legend: { 
            labelFormatter: function(label, series) {
                // series is the series object for the label
                if(label.lastIndexOf("#", 0) === 0)
                    return null;
                return label;
            }
        }
    };

    dataSeriesCollection = [];
    for (sensorIdx in sensorsIds) {
        // console.log("Plotting " + sensorsIds[sensorIdx]);
        dataSeries = {};

        // check data continuity here (check timestamp)
        var continuousData = [];
        var currentTime = new Date().getTime();
        for(var i = 0; i < series[sensorsIds[sensorIdx]].length; i++) {
            // console.log("dif: " + " = " + (currentTime - series[sensorsIds[sensorIdx]][i][0]));
            if(currentTime - series[sensorsIds[sensorIdx]][i][0] < DECAY)
                continuousData.push(series[sensorsIds[sensorIdx]][i]);
        }
        
        dataSeries.data = continuousData;
        dataSeries.label = sensorsIds[sensorIdx];
        dataSeriesCollection.push(dataSeries);
    }

    var plotObj = $.plot($(chartId), dataSeriesCollection, options);
}