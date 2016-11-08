function get_modal_file(url, id, div_content){

    $.get(url, function (data) {
        $(div_content).detach();
        $(div_content).append(data);
        $(id).modal('show');
    });

}
