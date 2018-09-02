$(function () {
	$(document).on('show.bs.collapse', ".alternative-panel-content", function () {
		$(this).parent().find('i.fa-angle-right').switchClass("fa-angle-right", "fa-angle-down", 250, "easeInOutQuad");
	});

	$(document).on('hide.bs.collapse', ".alternative-panel-content", function () {
		$(this).parent().find('i.fa-angle-down').switchClass("fa-angle-down", "fa-angle-right", 250, "easeInOutQuad");
	});
});

function delete_question(url, question) {
	$('.modal').remove();

	$.get(url, function (modal) {
		$(question).parent().after(modal);

		$('.modal').modal('show');
	});
}