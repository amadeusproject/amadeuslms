// loadOnScroll handler
var loadOnScroll = function() {
   // If the current scroll position is past out cutoff point...
    if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
        // temporarily unhook the scroll event watcher so we don't call a bunch of times in a row
        $(window).unbind();
        // execute the load function below that will visit the view and return the content
        loadItems();
    }
};

var loadItems = function() {
    // Check if page is equal to the number of pages
    if (pageNum == numberPages) {
        return false
    }
    // Update the page number
    pageNum = pageNum + 1;

    $("#loading").show();
    // Configure the url we're about to hit
    setTimeout(function (){
        $.ajax({
            url: baseUrl,
            data: {'page': pageNum},
            success: function(data) {
                $("#loading").hide();

                $("#timeline").append(data);
            },
            complete: function(data, textStatus){
                // Turn the scroll monitor back on
                $(window).bind('scroll', loadOnScroll);
            }
        });
    }, 1000)
};

$(document).ready(function(){
   $(window).bind('scroll', loadOnScroll);
   $.material.init();
});