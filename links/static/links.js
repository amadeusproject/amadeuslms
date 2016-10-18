function get_modal_link(url, id,div_content){
    $.get(url, function (data) {
        //alert(data);
        // $(div_content).empty();
        // $(div_content).append(data);
        $(id).modal('show');
    });

}
