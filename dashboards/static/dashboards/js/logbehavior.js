/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

$(document).ready(function(){
	d = new Date();
	d.setDate(d.getDate() - 30);
	$('#init_date').datetimepicker({
		defaultDate: d,
		format: 'L'
	});
    $('#end_date').datetimepicker({
        useCurrent: false, //Important! See issue #1075
        defaultDate: new Date(),
        format: 'L'
    });
    $("#init_date").on("dp.change", function (e) {
        $('#end_date').data("DateTimePicker").minDate(e.date);
       	$('#search').removeClass("disabled");
    });
    $("#end_date").on("dp.change", function (e) {
        $('#init_date').data("DateTimePicker").maxDate(e.date);
     	$('#search').removeClass("disabled");
    });
    //initialize the table with log from last 30 days
    init_date = $("#init_date").data("DateTimePicker").date();
   	end_date = $("#end_date").data("DateTimePicker").date();
   	log.refresh_log_data(init_date, end_date);

   	$("#search").click(function(){
   		if (!$("#search").hasClass("disabled")){
	   		init_date = $("#init_date").data("DateTimePicker").date();
		   	end_date = $("#end_date").data("DateTimePicker").date();
		   	log.refresh_log_data(init_date, end_date);
	     	$('#search').addClass("disabled");
     	}

   	});
});




var log = {
	
	refresh_log_data: function(init_date, end_date){
		$.get("/dashboards/get_log_data", {init_date: init_date.format("YYYY-MM-DD"), end_date: end_date.format("YYYY-MM-DD")}).done(function(data){
			log.render_table("log-body", data);
		})
	},
	render_table: function(target_id, data){
		table_body = $('#' + target_id);

		tables = $('#log-table_wrapper');
		if (tables.length > 0){
			$(tables).remove();
		}


		content = "<table id='log-table' class='table table-striped table-bordered'>";
		//load row names at the top 
		content += "<thead><th> Datetime </th> <th> Usuário </th> <th> Components </th> <th> Recurso </th><th> Ação </th>"
			+ "<th> Categoria </th> <th> Assunto </th> <th> Contexto </th></thead>"
		//build row html data
		data.forEach(function(datum){
			content += "<tr>" + html_helper.row_builder(datum) + "</tr>";
		});

		content += "</table>";

		$(table_body).append(content);

		/*$('#log-table').hpaging({
			"limit": 20, //maximum number of elements per page
		});*/

		$('#log-table').DataTable({
			"pageLength": 100
		});

	},
}


var html_helper = {
	row_builder: function(datum){
		//build each table row for each log record
		result = "";
		result = "<td>" + datum.datetime + "</td>" + "<td>" + datum.user + "</td>" + "<td>" + datum.component + "</td>"
		+ "<td>" + datum.resource + "</td>" + "<td>" + datum.action + "</td>" + "<td>" + datum.context.category_name + "</td>"
		+ "<td>" + datum.context.subject_name + "</td>" + "<td>"+ datum.context + "</td>";
		return result;
	}
}