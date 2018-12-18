// author: qffa


// jquery post callback function, used in modal form
function submitForm(event) {
    event.preventDefault();
    var $form =$(this),
        url = $form.attr("action"),
        data = $form.serialize();
    var posting = $.post(url, data);
    $("#loading-effect").modal("show");
    posting.done(function(data) {
        $("#loading-effect").modal("hide");
        if ($(data).find("#navbar").length > 0) {
            $form.parents(".modal").modal("hide");
            var content = $(data).find(".row");
            $(".row").empty().append(content);
        }
        else {
            $form.parents(".modal").empty().append(data);
        }
    })
    posting.fail(function(jqXHR) {
        //$("html").empty().append(jqXHR.responseText);
        $("html").empty().append("error happens");
    
    })
}
