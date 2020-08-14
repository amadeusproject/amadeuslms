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
        `${data["active_students"]}`
    );
    $("#number-teacher-active").html(
        `${data["active_teachers"]}`
    );
    $("#teacher-percent-value").html(
        active_teachers_percent_value
    );
    $("#students-percent-value").html(
        active_students_percent_value
    );
    $("#number-students-inactive").html(
        inactive_students
    );
    $("#number-teacher-inactive").html(
        inactive_teachers
    );
    $("#percent-teacher-value").html(
        inactive_teachers_percent_value
    );
    $("#percent-students-value").html(
        inactive_students_percent_value
    );
    
    $("#students-percent-2").css(
        "height", `${6*active_students_percent_value/100}em`
    );
    $("#teacher-percent-2").css(
        "height", `${6*active_teachers_percent_value/100}em`
    );
    
    
    $("#percent-teacher-inactive-2").css(
        "height", `${6*inactive_teachers_percent_value/100}em`
    );
    $("#percent-students-inactive-2").css(
        "height", `${6*inactive_students_percent_value/100}em`
    );

    if(active_students_percent_value < 15){
        $("#students-percent-value").html(
            `<p>${active_students_percent_value}</p>`
        );
  
    }
    
    if(active_teachers_percent_value < 15){
        $("#teacher-percent-value").html(
            `<p>${active_teachers_percent_value}</p>`
        );
    }

    if(inactive_students_percent_value < 15){
        $("#percent-students-inactive-2").html(
            `<p>${active_students_percent_value}</p>`
        );
  
    }
    
    if(inactive_teachers_percent_value < 15){
        $("#percent-teacher-inactive-2").html(
            `<p>${inactive_teachers_percent_value}</p>`
        );
    }


}