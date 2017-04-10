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

    $(".clear_filter").click(function () {
        var frm = $(this).parent();

        frm.find("input[type='checkbox']").prop('checked', false);

        frm.submit();
    });
});