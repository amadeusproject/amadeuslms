$(function() {
    const usersgraphUrl = $(".usersgraph").data("url");
    
    loadBarChartData(usersgraphUrl, $("#from").val(), $("#until").val());
    
    
});

function loadBarChartData(usersgraphUrl, dataIni, dataEnd){
    
    $.get(usersgraphUrl, { data_ini: dataIni, data_end: dataEnd }, dataset => {
        drawBarChart(dataset);
    });

}
      

function drawBarChart(data){
    let active_teachers_percent_value = (data["active_teachers"]/data["total_teachers"]*100).toFixed(0)
    let active_students_percent_value = (data["active_students"]/data["total_students"]*100).toFixed(0)
    let inactive_teachers = data["total_teachers"]-data["active_teachers"]
    let inactive_students =data["total_students"]-data["active_students"]
    let inactive_teachers_percent_value = (inactive_teachers/data["total_teachers"]*100).toFixed(0)
    let inactive_students_percent_value = (inactive_students/data["total_students"]*100).toFixed(0)
    
    $("#legend_teacher").html(
        `Professores (${data["total_teachers"]})`
    );
    $("#legend_students").html(
        `Estudantes (${data["total_students"]})`
    );
    $("#number-students-active").html(
        `<p style="margin-top:0.3em" data-toggle="tooltip" data-placement="bottom" title="${data["active_students"]} dos ${data["total_students"]} estudantes estão ativos no período selecionado">${data["active_students"]}</p>`
    );
    $("#number-teacher-active").html(
        `<p style="margin-top:0.3em" data-toggle="tooltip" data-placement="bottom" title="${data["active_teachers"]} dos ${data["total_teachers"]} professores estão ativos no período selecionado">${data["active_teachers"]}</p>`
    );
    $("#teacher-percent-value").html(
        `<p data-toggle="tooltip" data-placement="bottom" title="${active_teachers_percent_value}% dos  professores estão ativos no período selecionado">${active_teachers_percent_value}%</p>`
    );
    $("#students-percent-value").html(
        `<p data-toggle="tooltip" data-placement="bottom" title="${active_students_percent_value}% dos  estudantes estão ativos no período selecionado">${active_students_percent_value}%</p>`
    );
    $("#number-students-inactive").html(
        `<p style="margin-top:0.3em" data-toggle="tooltip" data-placement="bottom" title="${inactive_students} dos ${data["total_students"]} estudantes estão inativos no período selecionado">${inactive_students}</p>`
    );
    $("#number-teacher-inactive").html(
        `<p style="margin-top:0.3em" data-toggle="tooltip" data-placement="bottom" title="${inactive_teachers} dos ${data["total_teachers"]} professores estão inativos no período selecionado">${inactive_teachers}</p>`
    );
    $("#percent-teacher-value").html(
        `<p data-toggle="tooltip" data-placement="bottom" title="${inactive_teachers_percent_value}% dos professores estão inativos no período selecionado">${inactive_teachers_percent_value}%</p>`
    );
    $("#percent-students-value").html(
        `<p data-toggle="tooltip" data-placement="bottom" title="${inactive_students_percent_value}% dos estudantes estão inativos no período selecionado">${inactive_students_percent_value}%</p>`
    );
    
    $("#students-percent-2").css(
        "height", `${6*active_students_percent_value/100}em`
    );
    $("#teacher-percent-2").css(
        "height", `${6*active_teachers_percent_value/100}em`
    );
    
    
    $("#percent-teacher-inactive-2").css(
        "height", `${6*inactive_teachers_percent_value/100}em`
    ).css("margin-bottom", "15");
    $("#percent-students-inactive-2").css(
        "height", `${6*inactive_students_percent_value/100}em`
    );

    if(active_students_percent_value < 25){
        $("#students-percent-value").html(
            `<p style="margin-bottom:1.5em;" data-toggle="tooltip" data-placement="bottom" title="${active_students_percent_value}% dos estudantes estão ativos no período selecionado">${active_students_percent_value}%</p>`
        );

        
        
  
    }
    
    if(active_teachers_percent_value < 25){
        $("#teacher-percent-value").html(
            `<p style="margin-bottom:1.5em;" data-toggle="tooltip" data-placement="bottom" title="${active_teachers_percent_value}% dos professores estão ativos no período selecionado">${active_teachers_percent_value}%</p>`
        );
        
    }

    if(inactive_students_percent_value < 25){
        $("#percent-students-inactive-2").html(
            `<p style="margin-bottom:1.5em;" data-toggle="tooltip" data-placement="bottom" title="${inactive_students_percent_value}% dos estudantes estão inativos no período selecionado">${active_students_percent_value}%</p>`
        );
        
  
    }
    
    if(inactive_teachers_percent_value < 25){
        $("#percent-teacher-inactive-2").html(
            `<p style=margin-bottom:1.5em;" data-toggle="tooltip" data-placement="bottom" title="${inactive_teachers_percent_value}% dos professores estão inativos no período selecionado">${inactive_teachers_percent_value}%</p>`
        );
        
    }

    $("#panel_loading_mask1").hide();
    $("#panel_loading_mask2").hide();
}