/* 
Copyright 2016, 2017 UFPE - Universidade Federal de Pernambuco
 
Este arquivo é parte do programa Amadeus Sistema de Gestão de Aprendizagem, ou simplesmente Amadeus LMS
 
O Amadeus LMS é um software livre; você pode redistribui-lo e/ou modifica-lo dentro dos termos da Licença Pública Geral GNU como publicada pela Fundação do Software Livre (FSF); na versão 2 da Licença.
 
Este programa é distribuído na esperança que possa ser útil, mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a Licença Pública Geral GNU para maiores detalhes.
 
Você deve ter recebido uma cópia da Licença Pública Geral GNU, sob o título "LICENSE", junto com este programa, se não, escreva para a Fundação do Software Livre (FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
*/

// loadOnScroll handler
var loadOnScroll = function() {
   // If the current scroll position is past out cutoff point...
    if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
        // temporarily unhook the scroll event watcher so we don't call a bunch of times in a row
        $(window).unbind();
        // execute the load function below that will visit the view and return the content
        loadPosts();
    }
};

var loadPosts = function() {
    var loadUrl = $('.mural').data('url'),
        pageNum = $('.mural').data('page'),
        numberPages = $('.mural').data('pages'),
        favorites = $('.mural').data('fav'),
        mine = $('.mural').data('mine'),
        showing = new_posts.join(',');
    // Check if page is equal to the number of pages
    if (pageNum == numberPages) {
        return false
    }
    // Update the page number
    pageNum = pageNum + 1;

    $("#loading_posts").show();
    // Configure the url we're about to hit
    setTimeout(function (){
        $.ajax({
            url: loadUrl,
            data: {'page': pageNum, "favorite": favorites, "mine": mine, "showing": showing},
            success: function(data) {
                $("#loading_posts").hide();

                $(".posts").append(data);

                $('.mural').data('page', pageNum);

                setTimeout(function () { postHeightLimits() }, 10);
            },
            complete: function(data, textStatus){
                // Turn the scroll monitor back on
                $(window).bind('scroll', loadOnScroll);
            }
        });
    }, 1000)
};

$(function () {
    $(window).bind('scroll', loadOnScroll);

    $("input[name='favorite']").on('change', function () {
        var checked = $(this).is(':checked');

        $("input[name='favorite']").each(function () {
            $(this).prop('checked', checked);
        });

        $("#post-filters").submit();
    });

    $("input[name='mine']").on('change', function () {
        var checked = $(this).is(':checked');

        $("input[name='mine']").each(function () {
            $(this).prop('checked', checked);
        });

        $("#post-filters").submit();
    });

    $(".clear_filter").click(function () {
        var frm = $(this).parent();

        frm.find("input[type='checkbox']").prop('checked', false);

        frm.submit();
    });
});