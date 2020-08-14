function loadLogsGraph(url, dataIni, dataEnd) {
    $.get(url, { data_ini: dataIni, data_end: dataEnd }, dataset => {
    $(".logs_chart").html(dataset["div"]);
    $(".logsgraph .info").append(`<p class='text-cloudy-legend' style="margin-right:25%"> Mínimo diário: ${dataset['min']} </p>     <p class='text-cloudy-legend' style="margin-right:25%">Máximo diário: ${dataset["max"]}</p>            <p class='text-cloudy-legend'>Total: ${dataset["total"]}</p>`)
    }
 );
}


$(function() {
    const logsGraphUrl = $(".logsgraph").data("url");
    loadLogsGraph(logsGraphUrl, $("#from").val(), $("#until").val())
    
   
    
});


      

