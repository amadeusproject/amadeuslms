function openTopic(url, topic, btn) {
    var icon = btn.find('i');
    var action = '', log_id;

    if (icon.hasClass('fa-caret-square-o-down')) {
        icon.removeClass('fa-caret-square-o-down');
        icon.addClass('fa-caret-square-o-up');
        action = 'open';
        log_id = -1;
    } else {
        icon.addClass('fa-caret-square-o-down');
        icon.removeClass('fa-caret-square-o-up');
        action = 'close';
        log_id = $(".topic_" + topic).find(".log_id").val();
    }

    $.ajax({
        url: url,
        data: {"action": action, "log_id": log_id},
        dataType: 'json',
        success: function (data) {
           if (action == 'open') {
                $(".topic_" + topic).find(".log_id").val(data.log_id);           
           }
        },
        error: function(data) {
            console.log('Error');
        }
    });
}