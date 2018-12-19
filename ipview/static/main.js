// author: qffa


// jquery post callback function, used in modal form
function submitForm(event) {
    event.preventDefault();
    var $form =$(this),
        url = $form.attr("action"),
        data = $form.serialize();
    $form.parents(".modal").modal("hide");
    $("#loading-effect").modal("show");
    var posting = $.post(url, data);
    posting.done(function(data) {
        $("#loading-effect").modal("hide");
        if ($(data).find("#navbar").length > 0) {
            var content = $(data).find(".row");
            $(".row").empty().append(content);
        }
        else {
            $form.parents(".modal").empty().append(data);
        }
    })
    posting.fail(function(jqXHR, textStatus, errorThrown) {
        //$("html").empty().append(jqXHR.responseText);
        $("html").empty().append(errorThrown);
    })
}
