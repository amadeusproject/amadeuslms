/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

/*
*
* Function to get a cookie stored on browser
*
*/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
/*
*
* Function to subscribe (works for courses and subjects)
*
*/
function subscribe(elem, url, id, confirm_message) {
	alertify.confirm(confirm_message, function(){
		$.ajax({
			dataType: "json",
			url: url,
			success: function (data) {
				if (data.status == "ok") {
					elem.remove();
					alertify.success(data.message);
					$(".panel_"+id).find(".view_btn").show()
				} else {
					alertify.error(data.message);
				}
			}
		});
	});
}

/*
*
* Function to delete a course
*
*/

var RemoveCourse = {
  remove: function(url,dados,id_li_link){
    $('#category').modal().hide();
      $.post(url,dados, function(data){
        $(id_li_link).remove();
        // alert("certo");
        $('body').removeClass('modal-open');
        $("#modal_course").empty();
        $(".modal-backdrop.in").remove();
        alertify.success("Course removed successfully!");
        // setTimeout(function () { location.reload(1); }, 1);
      }).fail(function(){
        $("#modal_course").empty();
        $("#modal_course").append(data);
        $('#course').modal('show');
      });
  }
}

var delete_course = {
  get: function (url, id_modal, id_div_modal){
    $.get(url, function(data){
      if($(id_modal).length){
        $(id_div_modal).empty();
        $(id_div_modal).append(data);
      } else {
        $(id_div_modal).append(data);
      }
      $(id_modal).modal('show');
    });
  }
};

/*
*
* Function to load create course's form
*
*/
function replicate_course(url, course) {
    $.ajax({
        url: url,
        data: {'form': course},
        success: function(data) {
            $(".course_replicate_form").html(data);
        }
    });
}

/*
*
* Functions to control category marker
*
*/
$(function () {
    bindCollapse();
});

function bindCollapse() {
    $('.collapse').on('show.bs.collapse', function (e) {
        if($(this).is(e.target)){
            var btn = $(this).parent().find('.fa-angle-right');

            btn = btn[0];

            $(btn).switchClass("fa-angle-right", "fa-angle-down", 250, "easeInOutQuad");

            var url = $(this).parent().find('.log_url').val();
            var log_input = $(this).parent().find('.log_id');

            if (typeof(url) != 'undefined') {
                $.ajax({
                    url: url,
                    data: {'action': 'open'},
                    dataType: 'json',
                    success: function (data) {
                        log_input.val(data.log_id);
                    },
                    error: function (data) {
                        console.log(data);
                    }
                });
            }

        }
    });

    $('.collapse').on('hide.bs.collapse', function (e) {
        if($(this).is(e.target)){
            var btn = $(this).parent().find('.fa-angle-down');

            btn = btn[0];

            $(btn).switchClass("fa-angle-down", "fa-angle-right", 250, "easeInOutQuad");

            var url = $(this).parent().find('.log_url').val();
            var log_id = $(this).parent().find('.log_id').val();

            if (typeof(url) != 'undefined') {
                $.ajax({
                    url: url,
                    data: {'action': 'close', 'log_id': log_id},
                    dataType: 'json',
                    success: function (data) {
                        console.log(data.message);
                    },
                    error: function (data) {
                        console.log(data);
                    }
                });
            }
        }
    });
}

$('.category-panel-content').on('shown.bs.collapse', function(e) {
    if($(this).is(e.target)){
        var panel_id = $(this).attr('id');
        var holder = $(this).find('.holder');

        if ($('#' + panel_id + '-accordion').children().length == 0) {
            var load_sub_url = $(this).find('.load_sub_url').val();

            $.ajax({
                url: load_sub_url,
                success: function (data) {
                    $("#" + panel_id + "_loading").hide();
                    $('#' + panel_id + '-accordion').html(data);

                    var items = $('#' + panel_id + '-accordion').children(":visible").length;

                    if (items > 10) {
                        holder.jPages({
                            containerID : panel_id + "-accordion",
                            perPage: 10,
                            previous: "«",
                            next: "»",
                            midRange: 5
                        });
                    }

                    $('[data-toggle="tooltip"]').tooltip({
                        trigger: 'hover'
                    });

                    bindCollapse();
                }
            });
        } else {
            var items = $('#' + panel_id + '-accordion').children(":visible").length;

            if (items > 10) {
                holder.jPages({
                    containerID : panel_id + "-accordion",
                    perPage: 10,
                    previous: "«",
                    next: "»",
                    midRange: 5
                });
            }
        }


    }
});

$('.category-panel-content').on('hidden.bs.collapse', function(e) {
    if($(this).is(e.target)){
        var panel_id = $(this).attr('id');
        var holder = $(this).find('.holder');

        var items = $('#' + panel_id + '-accordion').children(":visible").length;

        if (items > 10) {
            holder.jPages("destroy");
        }

        $(this).find('.panel-collapse.in').collapse('hide');
    }
});


function delete_group(url) {
    $('.modal').remove();

    $.get(url, function (modal) {
        $("#group-accordion").after(modal);

        $('.modal').modal('show');
    });
}
